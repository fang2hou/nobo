#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------
# Syllabus module of Nobo.
# Fang2hou @ 2/7/2018
# github: https://github.com/fang2hou/Nobo
# ----------------------------------------
import requests
import re
import json
from bs4 import BeautifulSoup as bs
from .lib import fixja

class syllabusUser(object):
	"""syllabus Class"""
	# Setting for syllabus
	syllabusHomePagePath = "https://campusweb.ritsumei.ac.jp/syllabus/sso/KJgSearchTop.do"

	def __init__(self, username, password):
		self.rainbowID = username
		self.rainbowPassword = password
		self.webSession = requests.Session()
		self.syllabusList = {}

	def login(self):
		# Load first page using the webSession initialized before
		firstPage = self.webSession.get(self.syllabusHomePagePath)
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
		self.webSession.post(thirdPagePath, thirdPagePostData)

	def getSyllabusById(self, courseYear, courseID):
		self.syllabusList = {}

		syllabusAllInfoPagePath = "https://syllabus.ritsumei.ac.jp/syllabus/sso/SyShowAll.do"

		# Get all information about this course with (sylNendo, jyugyocd, kinouID)
		postData = {
			"mkjgkbcd": "",
			"daibuncd": "",
			"tyubuncd": "",
			"shobuncd": "",
			"sylNendo": courseYear,
			"jyugyocd": courseID,
			"kinouID": 'SKJ070',
		}

		# Save page source
		syllabusPage = self.webSession.post(syllabusAllInfoPagePath, postData)
		syllabusPageHeadTag = bs(syllabusPage.text, "html.parser")

		# FOR DEBUG
		# ---------------------------------
		# # get file and save -------------
		# syllabusPage = self.webSession.post(syllabusAllInfoPagePath, postData)
		# with open("temp.html", "w+") as f:
		# 	f.write(syllabusPage.text)
		# return 

		# # fake data ---------------------
		# with open("temp.html", "r") as inputFile:
		# 	syllabusPageHeadTag = bs(inputFile.read(), "html.parser")

		# Start of processing
		# Basic
		basicInfoTag = syllabusPageHeadTag.select(".jugyo_table")[0].find("tr").find_next_sibling("tr").find("td")
		courseNameString = fixja.removeLast(basicInfoTag.get_text().strip("\t\n "))
		courseNameString = fixja.convertHalfwidth(courseNameString)
		basicInfo = []

		if "  " in courseNameString:
			courseNames = courseNameString.split("  ")
			for courseName in courseNames:
				courseClass = re.findall(r"\([A-Za-z][0-9]\)", courseName)[0].strip("()")
				courseName = courseName.split(" (")[0]
				basicInfo.append({
					"name": courseName,
					"class": courseClass
				})
		else:
			courseName = courseNameString
			courseClass = re.findall(r"\([A-Za-z][0-9]\)", courseName)[0].strip("()")
			courseName = courseName.split(" (")[0]
			basicInfo.append({
				"name": courseName,
				"class": courseClass
			})

		# Semester
		semesterTag = basicInfoTag.find_next_sibling("td")
		semesterString = semesterTag.get_text()
		if "前期" in semesterString:
			courseSemester = "spring"
		elif "後期" in semesterString:
			courseSemester = "fall"
		else:
			courseSemester = "unknown"

		# Course Time
		courseTimeTag = semesterTag.find_next_sibling("td")
		courseTimeString = courseTimeTag.get_text().replace("\t", "").replace("\n", "")
		courseWeekday, courseArtPeriod, courseSciPeriod = re.findall(r"([月|火|水|木|金])([0-9]-[0-9]|[0-9])(\([0-9]-[0-9]\))", courseTimeString)[0]
		courseWeekday = fixja.convertWeekday(courseWeekday)
		courseSciPeriod = courseSciPeriod.strip("()")
		courseTime = {
			"year": courseYear,
			"semester": courseSemester,
			"weekday": courseWeekday,
			"period_art": courseArtPeriod,
			"period_sci": courseSciPeriod,
		}
		
		# Credit
		creditTag = courseTimeTag.find_next_sibling("td")
		credit = int(creditTag.get_text())

		# Teacher
		courseTeacherTag = creditTag.find_next_sibling("td")
		courseTeacherString = courseTeacherTag.get_text()
		courseTeacherString = fixja.removeLast(courseTeacherString.replace("\t", "").replace("\n", "").strip(" "))

		# Confirm if there are several teachers in list
		if "、" in courseTeacherString:
			hasSeveralTeachers = True
		else:
			hasSeveralTeachers = False

		if hasSeveralTeachers:
			courseTeacher = courseTeacherString.split("、")
		else:
			courseTeacher = [courseTeacherString]

		# Course Outline and Method
		outlineTag = syllabusPageHeadTag.find("dl")
		outline = fixja.removeLast(outlineTag.find("dd").get_text())
		
		# Student Attainment Objectives
		objectivesTag = outlineTag.find_next_sibling("dl")
		objectives = ""
		for subString in objectivesTag.find("dd").find_next_sibling("dd").contents:
			if str(subString) != "<br/>":
				objectives += subString.replace("\n", "").replace("\t", "")
			else:
				objectives += "\n"
		
		# Recommended Preparatory Course
		preCourseTag = objectivesTag.find_next_sibling("dl")
		precourse = fixja.removeLast(preCourseTag.find("dd").get_text())

		# Course Schedule
		scheduleTableTag = preCourseTag.find_next_sibling("dl")
		tempScheduleTableTag = scheduleTableTag.find("table").find("tr").find_next_sibling("tr")

		scheduleList = []

		while tempScheduleTableTag:
			# Lecture
			tempSchedule = {"lecture": int(tempScheduleTableTag.find("td").get_text()), "theme": fixja.removeLast(
				fixja.convertHalfwidth(tempScheduleTableTag.find("td").find_next_sibling("td").get_text()))}
			# Theme
			tempScheduleTableTag = tempScheduleTableTag.find_next_sibling("tr")
			# Keyword, References and Supplementary Information
			tempSchedule["references"] = fixja.removeLast(fixja.convertHalfwidth(tempScheduleTableTag.find("td").get_text()))
			tempScheduleTableTag = tempScheduleTableTag.find_next_sibling("tr")

			scheduleList.append(tempSchedule)
		
		# Recommendations for Private Study
		recommendationTag = scheduleTableTag.find_next_sibling("dl")
		recommendation = fixja.removeLast(recommendationTag.find("dd").get_text())
		
		# Grade Evaluation Method
		gradeEvaluationTag = recommendationTag.find_next_sibling("dl")
		gradeEveluationTableTag = gradeEvaluationTag.find("table")

		gradeEvaluation = {
			"note": "",
			"data": [],
		}

		gradeType = [
				"End of Semester Examination (Written)",
				"Report Examination",
				"Other"
		]

		gradeTypeIndex = 0

		for row in gradeEveluationTableTag.find_all("tr")[1:]:
			percentage = int(row.select(".percentage")[0].get_text().replace("%", ""))
			gradeNote = fixja.removeLast(row.select(".top")[0].get_text())
			gradeEvaluation["data"].append({
				"type": gradeType[gradeTypeIndex],
				"percentage": percentage,
				"note": gradeNote
			})
			gradeTypeIndex += 1

		gradeEvaluationNoteTag = gradeEveluationTableTag.find_next_sibling("dl")
		gradeEvaluationNote = gradeEvaluationNoteTag.find("dd").get_text()
		gradeEvaluationNote = fixja.removeLast(gradeEvaluationNote)
		gradeEvaluation["note"] = gradeEvaluationNote

		# Advice to Students on Study and Research Methods
		adviceTag = gradeEvaluationTag.find_next_sibling("dl")
		advice = fixja.removeLast(adviceTag.find("dd").get_text())

		# Textbooks
		textBookTag = adviceTag.find_next_sibling("dl")
		textBooks = {
			"note": "",
			"book": []
		}

		textBooksTable = textBookTag.find("table")
		if textBooksTable:
			for row in textBooksTable.find_all("tr")[1:]:
				tempTextBook = {}
				tempTag = row
				tempTag = tempTag.find("td")
				tempTextBook["title"] = fixja.removeLast(tempTag.get_text()).replace("\n", "")
				tempTag = tempTag.find_next_sibling("td")
				tempTextBook["author"] = fixja.removeLast(tempTag.get_text())
				tempTag = tempTag.find_next_sibling("td")
				tempTextBook["publisher"] = fixja.removeLast(tempTag.get_text())
				tempTag = tempTag.find_next_sibling("td")
				tempTextBook["ISBN"] = fixja.removeLast(tempTag.get_text()).replace("ISBN","")
				tempTag = tempTag.find_next_sibling("td")
				tempTextBook["comment"] = fixja.removeLast(tempTag.get_text())
				textBooks["book"].append(tempTextBook)
		textBooks["note"] = fixja.removeLast(textBookTag.find_all("dd", class_="nest")[0].get_text())

		# Reference Books
		refBookTag = textBookTag.find_next_sibling("dl")
		refBooks = {
			"note": "",
			"book": []
		}

		refBooksTable = refBookTag.find("table")
		if refBooksTable:
			for row in refBooksTable.find_all("tr")[1:]:
				tempRefBook = {}
				tempTag = row
				tempTag = tempTag.find("td")
				tempRefBook["title"] = fixja.removeLast(tempTag.get_text()).replace("\n", "")
				tempTag = tempTag.find_next_sibling("td")
				tempRefBook["author"] = fixja.removeLast(tempTag.get_text())
				tempTag = tempTag.find_next_sibling("td")
				tempRefBook["publisher"] = fixja.removeLast(tempTag.get_text())
				tempTag = tempTag.find_next_sibling("td")
				tempRefBook["ISBN"] = fixja.removeLast(tempTag.get_text()).replace("ISBN","")
				tempTag = tempTag.find_next_sibling("td")
				tempRefBook["comment"] = fixja.removeLast(tempTag.get_text())
				refBooks["book"].append(tempRefBook)
		refBooks["note"] = fixja.removeLast(refBookTag.find_all("dd", class_="nest")[0].get_text())
		
		# Web Pages for Reference
		refPageTag = refBookTag.find_next_sibling("dl")
		refPageStrings = refPageTag.find("dd").contents
		refPage = ""

		for refPageString in refPageStrings:
			afterString = fixja.removeLast(str(refPageString))
			if afterString != "":
				if "<a" in afterString:
					refPage += re.findall(r">(.+)<", afterString)[0]
					refPage += " "
				elif afterString == "<br/>":
					refPage = refPage[:-1] + "\n"
				else:
					refPage += afterString
					refPage += " "

		refPage = fixja.removeLast(refPage)

		# How to Communicate with the Instructor In and Out of Class(Including Instructor Contact Information)
		contactTag = refPageTag.find_next_sibling("dl")
		contactString = contactTag.find("dd")
		contactMethods = []

		for contactMethod in re.findall(r"<b>(.*)／", str(contactString)):
			contactMethods.append(fixja.removeLast(contactMethod))

		# Other Comments
		otherCommentsTag = contactTag.find_next_sibling("dl")
		otherComments = fixja.removeLast(otherCommentsTag.find("dd").get_text())

		# Save as dictionary
		self.syllabusList = {
			"basic": basicInfo,
			"time": courseTime,
			"teacher": courseTeacher,
			"credit": credit,
			"outline": outline,
			"objectives": objectives,
			"precourse": precourse,
			"schedule": scheduleList,
			"recommendation": recommendation,
			"grade_evluation": gradeEvaluation,
			"advice": advice,
			"text_books": textBooks,
			"ref_books": refBooks,
			"ref_pages": refPage,
			"contact_methods": contactMethods,
			"other_comments": otherComments,
		}

	def outputAsJSON(self, outputPath):
		if len(self.syllabusList) > 0:
			# Output data if the user has got information of all courses
			with open(outputPath, 'w+', encoding='utf8') as outfile:
				# Fix Kanji issue, set indent as 4
				json.dump(self.syllabusList, outfile, ensure_ascii=False, indent=4)
		else:
			# Notify when output without information of courses
			print("Use the getSyllabusById() method to get data first.")