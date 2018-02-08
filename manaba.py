#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------
# Manaba module of Nobo.
# Fang2hou @ 2/6/2018
# github: https://github.com/fang2hou/Nobo
# ----------------------------------------
import requests
from bs4 import BeautifulSoup as bs
import re
import json
from . import fixja

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
		forthPage = self.webSession.post(forthPagePath, forthPagePostData)

	def getCourseList(self):
		coursePage = self.webSession.get("https://ct.ritsumei.ac.jp/ct/home_course")
		coursePageCourseTable = bs(coursePage.text, "html.parser").select(".courselist")[0]

		# Initialize the output list
		self.courseList = []

		# Try to get each lesson information
		# The first -> 0, last 2 -> -2 is not a lesson (department notice, research etc.)
		for row in coursePageCourseTable.select(".courselist-c")[1:-2]:
			tempCourseInfo = {}

			lessonNameTag = row.find("td")
			
			# Convert the name into correct encode
			lessonName = lessonNameTag.select(".courselist-title")[0].get_text()
			lessonName = fixja.convertHalfwidth(lessonName)
			lessonName = fixja.removeNewLine(lessonName)

			# If the lesson has two names and codes, set the flag to process automatically
			if "§" in lessonName:
				hasTwoNames = True
			else:
				hasTwoNames = False

			# Split the code, name, and class information
			if hasTwoNames:
				lessonNames = lessonName.split("§")
				lessonCodes = {}
				lessonClasses = {}
				lessonCodes[0], lessonNames[0], lessonClasses[0] = splitLessonInfo(lessonNames[0])
				lessonCodes[1], lessonNames[1], lessonClasses[1] = splitLessonInfo(lessonNames[1])
			else:
				lessonCode, lessonName, lessonClass = splitLessonInfo(lessonName)

			# Update the basic node of tempCourseInfo
			if hasTwoNames:
				tempCourseInfo["basic"] = {}
				tempCourseInfo["basic"] = [{
					"name": lessonNames[0],
					"code": lessonCodes[0],
					"class": lessonClasses[0]
				},{
					"name": lessonNames[1],
					"code": lessonCodes[1],
					"class": lessonClasses[1]
				}]
			else:
				tempCourseInfo["two_names"] = "false";
				tempCourseInfo["basic"]  = [{
					"name": lessonName,
					"code": lessonCode,
					"class": lessonClass
				}]

			# Get the next node that contains the lesson year information
			lessonYearTag = lessonNameTag.find_next_sibling("td")
			lessonYear    = int(lessonYearTag.get_text())
			

			# Get the next node that contains lesson time and classroom information
			lessonTimeRoomTag = lessonYearTag.find_next_sibling("td")
			lessonTimeString  = lessonTimeRoomTag.find("span").get_text()
			
			# Get the semester information
			if "春" in lessonTimeString:
				lessonSemester = "spring"
			elif "秋" in lessonTimeString:
				lessonSemester = "fall"
			else:
				lessonSemester = "unknown"

			# Get the weekday and period information
			try:
				lessonWeekday, lessonPeriod = re.findall("(月|火|水|木|金)([0-9]-[0-9]|[0-9])", lessonTimeString)[0]
				lessonWeekday = fixja.convertWeekday(lessonWeekday)
			except:
				lessonWeekday, lessonPeriod = "unknown", "unknown"

			try:
				# Delete useless tags
				lessonTimeRoomTag.span.extract()
				lessonTimeRoomTag.br.extract()
			except:
				raise
			
			try:
				# Split the campus and room information
				lessonCampus, lessonRoom = re.findall("(衣笠|BKC|OIC) (.*)", lessonTimeRoomTag.get_text())[0]
				# Fix if "KIC" written in Kanji.
				lessonCampus = lessonCampus.replace("衣笠", "KIC")
			except:
				lessonCampus, lessonRoom = "unknown", "unknown"
			
			# Get teacher information
			lessonTeacherTag = lessonTimeRoomTag.find_next_sibling("td")
			lessonTeacherString = lessonTeacherTag.get_text()

			# Confirm if there are several teachers in list
			if "、" in lessonTeacherString:
				hasServeralTeachers = True
			else:
				hasServeralTeachers = False

			if hasServeralTeachers:
				lessonTeachers = lessonTeacherString.split("、")
			else:
				lessonTeacher = [lessonTeacherString]
			
			# Update information on temporary course information dictionary
			if hasServeralTeachers:
				tempCourseInfo["teacher"] = lessonTeachers
			else:
				tempCourseInfo["teacher"] = lessonTeacher

			tempCourseInfo["time"] = {
				"year": lessonYear,
				"semester": lessonSemester,
				"weekday": lessonWeekday,
				"period": lessonPeriod
			}
			tempCourseInfo["campus"] = lessonCampus
			tempCourseInfo["room"] = lessonRoom
			
			# Append the information of this course into output list
			self.courseList.append(tempCourseInfo)

	def outputJSON(self, outputPath):
		if len(self.courseList) > 0:
			# Output data if the user has got information of all courses
			with open(outputPath, 'w+', encoding='utf8') as outfile:
				# Fix Kanji issue, set indent as 4
				json.dump(self.courseList, outfile, ensure_ascii=False, indent=4)
		else:
			# Notify when output without information of courses
			print("Use the getCourseList() method to get data first.")