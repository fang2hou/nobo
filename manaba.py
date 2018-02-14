#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------
# Manaba module of Nobo
# Fang2hou @ 2/6/2018
# github: https://github.com/fang2hou/Nobo
# ----------------------------------------
import requests
import re
import json
from bs4 import BeautifulSoup as bs
from .lib import *

def splitLessonInfo(rawString):
	# Confirm no space to avoid regex rule
	rawString = rawString.replace(": ",":")
	# Use regex to get the name and code of the lesson
	code, name, classNumber = re.findall("([0-9]*):(.*)\(([A-Z][A-Z0-9])\)", rawString)[0]
	return code, name, classNumber

class manabaUser(object):
	"""manabaUser Class"""
	# Setting for manaba+R
	manabaHomePagePath = "https://ct.ritsumei.ac.jp/ct/home"

	def __init__(self, username, password):
		self.rainbowID = username
		self.rainbowPassword = password
		self.webSession = requests.Session()

	def login(self):
		# Load first page using the webSession initialized before
		firstPage = self.webSession.get(self.manabaHomePagePath)
		# Initialize the post data for second page
		secondPagePostData = {
			"USER": self.rainbowID,
			"PASSWORD": self.rainbowPassword
		}
		# Update the post data using the given information
		for inputElement in bs(firstPage.text, "html.parser").find_all('input'):
			tempAttrDict = inputElement.attrs
			if "name" in tempAttrDict and "value" in tempAttrDict:
				if tempAttrDict["name"] == "target":
					secondPagePostData["target"] = tempAttrDict["value"]
				elif tempAttrDict["name"] == "smauthreason":
					secondPagePostData["smauthreason"] = tempAttrDict["value"]
				elif tempAttrDict["name"] == "smquerydata":
					secondPagePostData["smquerydata"] = tempAttrDict["value"]
				elif tempAttrDict["name"] == "postpreservationdata":
					secondPagePostData["postpreservationdata"] = tempAttrDict["value"]
		
		# Load second page
		secondPage = self.webSession.post("https://sso.ritsumei.ac.jp/cgi-bin/pwexpcheck.cgi", secondPagePostData)
		# Get the redirect path
		thirdPagePath = "https://sso.ritsumei.ac.jp" + bs(secondPage.text, "html.parser").find('form').attrs["action"]
		# Create the post data for second page
		thirdPagePostData = {
			"USER": self.rainbowID,
			"PASSWORD": self.rainbowPassword,
			"smquerydata": secondPagePostData["smquerydata"],
		}

		# Load third page
		thirdPage = self.webSession.post(thirdPagePath, thirdPagePostData)
		# Initialize the post data for the forth page
		forthPagePostData = {}
		for inputElement in bs(thirdPage.text, "html.parser").find_all('input'):
			tempAttrDict = inputElement.attrs
			if "name" in tempAttrDict and "value" in tempAttrDict:
				if tempAttrDict["name"] == "RelayState":
					forthPagePostData["RelayState"] = tempAttrDict["value"].replace("&#x3a;",":").replace("&#x2f;","/"),
				elif tempAttrDict["name"] == "SAMLResponse":
					forthPagePostData["SAMLResponse"] = tempAttrDict["value"]
		# Evaluate the page of forth page
		forthPagePath = bs(thirdPage.text, "html.parser").find('form').attrs["action"].replace("&#x3a;",":").replace("&#x2f;","/")

		# Load forth page
		self.webSession.post(forthPagePath, forthPagePostData)

	def getCourseList(self):
		coursePage = self.webSession.get("https://ct.ritsumei.ac.jp/ct/home_course?chglistformat=list")

		coursePageCourseTable = bs(coursePage.text, "html.parser").select(".courselist")[0]

		# Initialize the output list
		self.courseList = []

		# Try to get each lesson information
		# The first -> 0, last 2 -> -2 is not a lesson (department notice, research etc.)
		for row in coursePageCourseTable.select(".courselist-c")[1:-2]:
			tempCourseInfo = {}

			lessonNameTag = row.find("td")
			
			# Convert the name into correct encode
			courseName = lessonNameTag.select(".courselist-title")[0].get_text()
			courseName = fixja.convertHalfwidth(courseName)
			courseName = fixja.removeNewLine(courseName)

			# If the lesson has two names and codes, set the flag to process automatically
			if "§" in courseName:
				hasTwoNames = True
			else:
				hasTwoNames = False

			# Split the code, name, and class information
			if hasTwoNames:
				courseNames = courseName.split("§")
				courseCodes = {}
				courseClasses = {}
				courseCodes[0], courseNames[0], courseClasses[0] = splitLessonInfo(courseNames[0])
				courseCodes[1], courseNames[1], courseClasses[1] = splitLessonInfo(courseNames[1])
				tempCourseInfo["basic"] = {}
				tempCourseInfo["basic"] = [{
					"name": courseNames[0],
					"code": int(courseCodes[0]),
					"class": courseClasses[0]
				}, {
					"name": courseNames[1],
					"code": int(courseCodes[1]),
					"class": courseClasses[1]
				}]
			else:
				courseCode, courseName, courseClass = splitLessonInfo(courseName)
				tempCourseInfo["two_names"] = "false"
				tempCourseInfo["basic"] = [{
					"name": courseName,
					"code": int(courseCode),
					"class": courseClass
				}]


			# Get the next node that contains the lesson year information
			courseYearTag = lessonNameTag.find_next_sibling("td")
			courseYear    = int(courseYearTag.get_text())
			

			# Get the next node that contains lesson time and classroom information
			courseTimeRoomTag = courseYearTag.find_next_sibling("td")
			courseTimeString  = courseTimeRoomTag.find("span").get_text()
			
			# Get the semester information
			if "春" in courseTimeString:
				courseSemester = "spring"
			elif "秋" in courseTimeString:
				courseSemester = "fall"
			else:
				courseSemester = "unknown"

			# Get the weekday and period information
			try:
				courseWeekday, coursePeriod = re.findall("([月|火|水|木|金])([0-9]-[0-9]|[0-9])", courseTimeString)[0]
				courseWeekday = fixja.convertWeekday(courseWeekday)
			except:
				courseWeekday, coursePeriod = "unknown", "unknown"

			try:
				# Delete useless tags
				courseTimeRoomTag.span.extract()
				courseTimeRoomTag.br.extract()
			except:
				raise
			
			try:
				# Split the campus and room information
				courseCampus, courseRoom = re.findall("(衣笠|BKC|OIC) (.*)", courseTimeRoomTag.get_text())[0]
				# Fix if "KIC" written in Kanji.
				courseCampus = courseCampus.replace("衣笠", "KIC")
			except:
				courseCampus, courseRoom = "unknown", "unknown"
			
			# Get teacher information
			courseTeacherTag = courseTimeRoomTag.find_next_sibling("td")
			courseTeacherString = courseTeacherTag.get_text()

			# Confirm if there are several teachers in list
			if "、" in courseTeacherString:
				courseTeachers = courseTeacherString.split("、")
				tempCourseInfo["teacher"] = courseTeachers
			else:
				courseTeacher = [courseTeacherString]
				tempCourseInfo["teacher"] = courseTeacher

			tempCourseInfo["time"] = {
				"year": courseYear,
				"semester": courseSemester,
				"weekday": courseWeekday,
				"period": coursePeriod
			}
			tempCourseInfo["campus"] = courseCampus
			tempCourseInfo["room"] = courseRoom
			
			# Append the information of this course into output list
			self.courseList.append(tempCourseInfo)

	def outputAsJSON(self, outputPath):
		if len(self.courseList) > 0:
			# Output data if the user has got information of all courses
			with open(outputPath, 'w+', encoding='utf8') as outfile:
				# Fix Kanji issue, set indent as 4
				json.dump(self.courseList, outfile, ensure_ascii=False, indent=4)
		else:
			# Notify when output without information of courses
			print("Use the getCourseList() method to get data first.")