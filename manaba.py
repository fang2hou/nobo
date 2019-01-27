# -*- coding: utf-8 -*-
# ----------------------------------------
# Nobo, a third-party Manaba API for Ritsumeikan
# 
# manaba.py
# Main Manaba module
# -------------------------------------------
# @Author  : Zhou Fang
# @Updated : 1/28/2018
# @Homepage: https://github.com/fang2hou/Nobo
# ----------------------------------------
import re
import json

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

from .lib import fixja
from .lib import base

def parse_course_info(raw_str):
	# Confirm no space to avoid regex rule
	raw_str = raw_str.replace(": ",":")
	# Use regex to get the name and code of the lesson
	info_str_format = r"([0-9]*):(.*)\(([A-Z]|[A-Z][0-9]|[0-9][A-Z])\)"
	code, name, class_order = re.findall(info_str_format, raw_str)[0]
	return code, name, class_order

def parse_course_time(raw_str):
	# Use regex to get the name and code of the lesson
	time_str_format = r"([月|火|水|木|金])([0-9])\(([0-9]{1,2})-([0-9]{1,2})\)"
	weekday, period, sci_period_start, sci_period_end = re.findall(time_str_format, raw_str)[0]
	return weekday, period, sci_period_start, sci_period_end

class ManabaUser(object):
	def __init__(self, username, password, config_path=None):
		# Initialize user data
		self.username = username
		self.password = password

		# Initialize configuration
		self.config   = base.load_config(path=config_path)
		self.cacheId  = base.convert_to_md5(self.username)
		self.isLogged = False
		
		# Initialize webdriver
		# NOTICE: Enable "headless" in release environment
		chrome_options   = Options()
		# chrome_options.add_argument("--headless")
		self.webdriver   = webdriver.Chrome(chrome_options=chrome_options)
		self.wait_time_out = WebDriverWait(self.webdriver, self.config["manaba"]["timeout"], self.config["manaba"]["login_attempt_interval"])

	def login(self):
		# Try to get the homepage of manaba
		self.webdriver.get(self.config["manaba"]["homepage"])

		# Confirm the current status, reduce the number of unnecessary login operations
		if not self.config["manaba"]["login_domain_root"] in self.webdriver.current_url:
			if self.config["manaba"]["domain_root"] in self.webdriver.current_url:
				# The page is not redirect to the login page, it shows Nobo is in
				print("Nobo: Already login. [User: %s]" % self.username)
				return True
		
		print("Nobo: Try to login... [User: %s]" % self.username)

		# Wait for login button rendering
		try:
			self.wait_time_out.until(lambda sign:self.webdriver.find_element_by_id("web_single_sign-on"))
		except:
			print("Nobo: Login timeout. [User: %s]" % self.username)
			return

		# Enter username
		inputElement = self.webdriver.find_element_by_xpath("//input[@name='USER']")
		inputElement.send_keys(self.username)

		# Enter password
		inputElement = self.webdriver.find_element_by_xpath("//input[@name='PASSWORD']")
		inputElement.send_keys(self.password)

		# Submit the form
		self.webdriver.find_element_by_xpath("//input[@id='Submit']").click()

		# Send a message if username or password is not correct
		if "AuthError" in self.webdriver.current_url:
			print("Nobo: Invalid ID or PASSWORD. [User: %s]")
			return False
	
		return True

	def get_course_list(self):
		# Parse the course page with html parser
		self.webdriver.get(self.config["manaba"]["homepage"]+"_course?chglistformat=list")
		course_page = self.webdriver.page_source
		course_table_body = bs(course_page, "html.parser").select(".courselist")[0]
		
		# Initialize the output list
		self.course_list = []

		# Try to get each lesson information
		# The first -> 0, last 2 -> -2 is not a lesson (department notice, research etc.)
		for course_table_line in course_table_body.select(".courselist-c"):

			# Initialize the course
			temp_course = {}

			# Academic year
			#------------------------------
			# If the acdemic year is missed, it shows this line is not a course, maybe a page
			academic_year_tag = course_table_line.find("td").find_next_sibling("td")
			if "" == academic_year_tag.get_text():
				continue
			else:
				academic_year = int(academic_year_tag.get_text())

			# Course name
			#------------------------------
			course_name_tag = course_table_line.find("td")
			# Convert the name into correct encode
			course_name_text = course_name_tag.select(".courselist-title")[0].get_text()
			course_name_text = fixja.convet_to_half_width(course_name_text)
			course_name_text = fixja.remove_newline(course_name_text)

			# If the lesson has two names and codes, set the flag to process automatically
			if "§" in course_name_text:
				# Split the code, name, and class information
				course_names = course_name_text.split("§")
				course_codes = {}
				course_classes = {}
				course_codes[0], course_names[0], course_classes[0] = parse_course_info(course_names[0])
				course_codes[1], course_names[1], course_classes[1] = parse_course_info(course_names[1])
				temp_course["basic"] = [{
					"code": int(course_codes[0]),
					"name": course_names[0],
					"class": course_classes[0]
				}, {
					"code": int(course_codes[1]),
					"name": course_names[1],
					"class": course_classes[1]
				}]
			else:
				course_code, course_name, course_class = parse_course_info(course_name_text)
				temp_course["basic"] = [{
					"code": int(course_code),
					"name": course_name,
					"class": course_class
				}]
			
			# Get the next node that contains lesson time and classroom information
			course_time_room_tag = academic_year_tag.find_next_sibling("td")
			course_time_text  = course_time_room_tag.find("span").get_text()
			
			# Get the semester information
			if "春" in course_time_text:
				courseSemester = "spring"
			elif "秋" in course_time_text:
				courseSemester = "fall"
			else:
				courseSemester = "unknown"

			# Get the weekday and period information
			try:
				courseWeekday, coursePeriod = re.findall(r"([月|火|水|木|金])([0-9]-[0-9]|[0-9])", course_time_text)[0]
				courseWeekday = fixja.convert_week_to_en(courseWeekday)
			except:
				courseWeekday, coursePeriod = "unknown", "unknown"

			try:
				# Delete useless tags
				course_time_room_tag.span.extract()
				course_time_room_tag.br.extract()
			except:
				raise
			
			try:
				# Split the campus and room information
				courseCampus, courseRoom = re.findall("(衣笠|BKC|OIC) (.*)", course_time_room_tag.get_text())[0]
				# Fix if "KIC" written in Kanji.
				courseCampus = courseCampus.replace("衣笠", "KIC")
			except:
				 courseRoom   = course_time_room_tag.get_text().strip()
				#  courseCampus = "unknown"
			
			# Get teacher information
			courseTeacherTag    = course_time_room_tag.find_next_sibling("td")
			courseTeacherString = courseTeacherTag.get_text()

			# Confirm if there are several teachers in list
			if "、" in courseTeacherString:
				courseTeachers = courseTeacherString.split("、")
				temp_course["teacher"] = courseTeachers
			else:
				courseTeacher = [courseTeacherString]
				temp_course["teacher"] = courseTeacher

			temp_course["time"] = {
				"year": academic_year,
				"semester": courseSemester,
				"weekday": courseWeekday,
				"period": coursePeriod
			}
			# tempCourseInfo["campus"] = courseCampus
			temp_course["room"] = courseRoom
			
			# Append the information of this course into output list
			self.course_list.append(temp_course)
		return

	def output_course_list(self, outputPath):
		if len(self.course_list) > 0:
			# Output data if the user has got information of all courses
			base.export_dict_as_json(outputPath, self.course_list)
		else:
			# Notify when output without information of courses
			print("Use the getCourseList() method to get data first.")