#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------
# Syllabus module of Nobo.
# Fang2hou @ 2/7/2018
# github: https://github.com/fang2hou/Nobo
# ----------------------------------------
import requests
from bs4 import BeautifulSoup as bs
from bs4 import UnicodeDammit as ud
import re
import json
import fixja

class syllabusUser(object):
	"""syllabus Class"""
	# Setting for syllabus
	syallabusHomePagePath = "https://campusweb.ritsumei.ac.jp/syllabus/sso/KJgSearchTop.do"

	def __init__(self, username, password):
		self.rainbowID = username
		self.rainbowPassword = password
		self.webSession = requests.Session()

	def login(self):
		# Load first page using the webSession initialized before
		firstPage = self.webSession.get(self.syallabusHomePagePath)
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

		# Credit
		creditTag = syllabusPageHeadTag.select(".jugyo_table")[0].find("tr").find_next_sibling("tr").find_all("td")[3]
		credit = int(creditTag.get_text())

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
			tempSchedule = {}
			# Lecture
			tempSchedule["lecture"] = int(tempScheduleTableTag.find("td").get_text())
			# Theme
			tempSchedule["theme"] = fixja.removeLast(fixja.convertHalfwidth(tempScheduleTableTag.find("td").find_next_sibling("td").get_text()))
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
		# TODO
		textBookTag = adviceTag.find_next_sibling("dl")
		textBook = fixja.removeLast(textBookTag.find("dd").get_text())
			# Note
		 
		# Reference Books
		# TODO
		refBookTag = textBookTag.find_next_sibling("dl")
			# Note


		# Web Pages for Reference
		# TODO
		refPagekTag = refBookTag.find_next_sibling("dl")
		refPage = fixja.removeLast(refPagekTag.find("dd").get_text())
		
		# How to Communicate with the Instructor In and Out of Class(Including Instructor Contact Information)
		contactTag = refPagekTag.find_next_sibling("dl")
		contactString = contactTag.find("dd")
		contactMethods = []

		for contactMethod in re.findall("<b>(.*)／", str(contactString)):
			contactMethods.append(fixja.removeLast(contactMethod))

		# Other Comments
		otherCommentsTag = contactTag.find_next_sibling("dl")
		otherComments = fixja.removeLast(otherCommentsTag.find("dd").get_text())

		# Save as dictionary
		self.syllabusList = {
			"credit": credit,
			"outline": outline,
			"objectives": objectives,
			"precourse": precourse,
			"schedule": scheduleList,
			"recommendation": recommendation,
			"grade_evluation": gradeEvaluation,
			"advice": advice,
			"contact_methods": contactMethods,
			"other_comments": otherComments,
		}

	def outputJSON(self, outputPath):
		if len(self.syllabusList) > 0:
			# Output data if the user has got information of all courses
			with open(outputPath, 'w+', encoding='utf8') as outfile:
				# Fix Kanji issue, set indent as 4
				json.dump(self.syllabusList, outfile, ensure_ascii=False, indent=4)
		else:
			# Notify when output without information of courses
			print("Use the getSyllabusById() method to get data first.")