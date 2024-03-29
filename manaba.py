# -*- coding: utf-8 -*-
# -------------------------------------------
# nobo, No Borders
#
# manaba.py
# Main Manaba module
# -------------------------------------------
# @Author  : Zhou Fang
# @Updated : 1/29/2019
# @Homepage: https://github.com/fang2hou/nobo
# -------------------------------------------
import sys
import re
import json

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

from . import fixja
from . import base

# -------------------------------------------
# Parser function
# -------------------------------------------


def parse_course_info(raw_str):
    raw_str = raw_str.replace(": ", ":")
    # Use regex to get the name and code of the course
    info_str_format = r"([0-9]*):(.*)\(([A-Z]|[A-Z][0-9]|[0-9][A-Z])\)"
    code, name, class_order = re.findall(info_str_format, raw_str)[0]
    return code, name, class_order


def parse_course_time(raw_str):
    try:
        # Science
        time_str_format = r"([月|火|水|木|金])([0-9]{1,2})\(([0-9]{1,2})-([0-9]{1,2})\)"
        weekday, period, sci_period_start, sci_period_end = re.findall(
            time_str_format, raw_str)[0]
    except:
        # Arts
        try:
            time_str_format = r"([月|火|水|木|金])([0-9]{1,2})"
            weekday, period = re.findall(time_str_format, raw_str)[0]
            sci_period_start, sci_period_end = "unknown", "unknown"
        except:
            weekday, period, sci_period_start, sci_period_end = "unknown", "unknown", "unknown", "unknown"

    weekday = fixja.translate_weekday(weekday)
    return weekday, period, sci_period_start, sci_period_end


def parse_course_room_with_campus(raw_str):
    # NOTICE: This function is unused since campus info has been deleted
    try:
        time_str_format = r"([衣笠|KIC|BKC|OIC]) ([.*])"
        campus, room = re.findall(time_str_format, raw_str)[0]
        # Fix if "KIC" written in Kanji.
        campus = campus.replace("衣笠", "KIC")
    except:
        # Other course
        campus, room = "unknown", "unknown"

    return campus, room


class RitsStudent(object):
    # -------------------------------------------
    # RitsStudent Class
    # -------------------------------------------
    def __init__(self, username, password, config_path=None, webdriver_path=None):
        # Initialize user data
        self.username = username
        self.password = password

        # Initialize configuration
        self.config = base.load_config(path=config_path)
        self.cacheId = base.convert_to_md5(self.username)
        self.isLogged = False

        # Initialize webdriver
        # NOTICE: Enable "headless" in release environment
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")

        if None == webdriver_path:
            webdriver_path = sys.path[0]+"/chromedriver"

        self.webdriver = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=webdriver_path)
        self.wait_time_out = WebDriverWait(
            self.webdriver, self.config["manaba"]["timeout"], self.config["manaba"]["login_attempt_interval"])

    def login(self):
        # Try to get the homepage of manaba
        self.webdriver.get(self.config["manaba"]["homepage"])

        # Confirm the current status, reduce the number of unnecessary login operations
        if not self.config["manaba"]["login_domain_root"] in self.webdriver.current_url:
            if self.config["manaba"]["domain_root"] in self.webdriver.current_url:
                # The page is not redirect to the login page, it shows Nobo is in
                base.debug_print(
                    "[nobo][{}] Already login.".format(self.username))
                return True

        base.debug_print("[nobo][{}] Try to login...".format(self.username))

        # Wait for login button rendering
        try:
            self.wait_time_out.until(
                lambda sign: self.webdriver.find_element_by_id("web_single_sign-on"))
        except:
            base.debug_print("[nobo][{}] Login timeout.".format(self.username))
            return

        # Enter username
        inputElement = self.webdriver.find_element_by_xpath(
            "//input[@name='USER']")
        inputElement.send_keys(self.username)

        # Enter password
        inputElement = self.webdriver.find_element_by_xpath(
            "//input[@name='PASSWORD']")
        inputElement.send_keys(self.password)

        # Submit the form
        self.webdriver.find_element_by_xpath("//input[@id='Submit']").click()

        # Send a message if username or password is not correct
        if "AuthError" in self.webdriver.current_url:
            base.debug_print(
                "[nobo][{}]  Invalid ID or PASSWORD. ".format(self.username))
            return False

        return True

    def get_course_list(self):
        if not self.login():
            base.debug_print(
                "[nobo][{}] Error: Login process is failed.".format(self.username))
            return

        base.debug_print(
            "[nobo][{}] Login successful, start to get courses.".format(self.username))
        self.webdriver.get(
            self.config["manaba"]["homepage"]+"_course?chglistformat=list")
        course_page = self.webdriver.page_source
        course_table_body = bs(
            course_page, "html.parser").select(".courselist")[0]

        # Initialize the output list
        course_list = []

        # Try to get each course information
        # The first -> 0, last 2 -> -2 is not a course (department notice, research etc.)
        base.debug_print(
            "[nobo][{}] Start to parse table of courses.".format(self.username))
        for course_table_line in course_table_body.select(".courselist-c"):

            # Initialize the course
            temp_course = {}

            # Academic year
            # -------------------------------------------
            # If the acdemic year is missed, it shows this line is not a course, maybe a page
            academic_year_tag = course_table_line.find(
                "td").find_next_sibling("td")
            if "" == academic_year_tag.get_text():
                continue
            else:
                academic_year = int(academic_year_tag.get_text())

            # Course name
            # -------------------------------------------
            course_name_tag = course_table_line.find("td")
            # Convert the name into correct encode
            course_name_text = course_name_tag.select(
                ".courselist-title")[0].get_text()
            course_name_text = fixja.convet_to_half_width(
                course_name_text).strip()

            # If the course has two names and codes, set the flag to process automatically
            if "§" in course_name_text:
                # Split the code, name, and class information
                course_names = course_name_text.split("§")
                course_codes = {}
                course_classes = {}
                course_codes[0], course_names[0], course_classes[0] = parse_course_info(
                    course_names[0])
                course_codes[1], course_names[1], course_classes[1] = parse_course_info(
                    course_names[1])
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
                course_code, course_name, course_class = parse_course_info(
                    course_name_text)
                temp_course["basic"] = [{
                    "code": int(course_code),
                    "name": course_name,
                    "class": course_class
                }]

            # Course time
            # -------------------------------------------
            # Get the next node that contains course time and classroom information
            course_time_room_tag = academic_year_tag.find_next_sibling("td")
            course_time_text = course_time_room_tag.find("span").get_text()

            if "春" in course_time_text:
                course_semester = "spring"
            elif "秋" in course_time_text:
                course_semester = "fall"
            else:
                course_semester = "unknown"

            course_weekday, course_period, course_sci_period_start, course_sci_period_end = parse_course_time(
                course_time_text)

            temp_course["time"] = {
                "year": academic_year,
                "semester": course_semester,
                "weekday": course_weekday,
                "period": course_period,
                "sci_period_start": course_sci_period_start,
                "sci_period_end": course_sci_period_end,
            }

            # Course room
            # -------------------------------------------
            # Delete time tags
            try:
                course_time_room_tag.span.extract()
                course_time_room_tag.br.extract()
                course_room = course_time_room_tag.get_text().strip()
            except:
                base.debug_print(
                    "[nobo][{}] Something wrong with deleting useless tags.".format(self.username))
                course_room = "unknown"
            temp_course["room"] = course_room

            # Course teacher
            # -------------------------------------------
            course_teacher_tag = course_time_room_tag.find_next_sibling("td")
            course_teacher_text = course_teacher_tag.get_text()

            # Confirm if there are several teachers in list
            if "、" in course_teacher_text:
                course_teachers = course_teacher_text.split("、")
                temp_course["teacher"] = course_teachers
            else:
                course_teacher = [course_teacher_text]
                temp_course["teacher"] = course_teacher

            # Append the information of this course into output list
            course_list.append(temp_course)

        base.debug_print("[nobo][{}] Course list got.".format(self.username))

        return course_list

    def get_emergency_announcements(self, page_source):
        emergency_announcements = []

        emergency_announcement_table_rows = bs(
            page_source, "html.parser").select(
            "#kinkyudata > div.my-infolist-body > table > tbody > tr")

        for row in emergency_announcement_table_rows:
            element_dict = {}
            element_dict["date"] = row.select("td")[0].get_text().strip()
            element_dict["title"] = row.select(
                "td")[1].select("div > a")[0].get_text()
            element_dict["from"] = ""
            emergency_announcements.append(element_dict)

        base.debug_print(
            "[nobo][{}] Emergency announcements got.".format(self.username))

        return emergency_announcements

    def get_announcements_to_individual(self, page_source):
        announcements_to_individual = []

        announcements_to_individual_table_rows = list(bs(
            page_source, "html.parser").select("#announcementlistdiv > table > tbody > tr"))

        for i in range(len(announcements_to_individual_table_rows)-1):
            row = announcements_to_individual_table_rows[i]
            element_dict = {}
            element_dict["date"] = row.select("td")[0].get_text().strip()
            element_dict["title"] = row.select(
                "td")[1].select("div > a")[0].get_text()
            element_dict["from"] = row.select(
                "td")[2].get_text().strip()
            announcements_to_individual.append(element_dict)

        base.debug_print(
            "[nobo][{}] Announcements to individual got.".format(self.username))

        return announcements_to_individual

    def get_other_announcements(self, page_source):
        other_announcements = []

        other_announcements_table_rows = list(bs(
            page_source, "html.parser").select("#pubannouncementlistdiv > table > tbody > tr"))

        for row in other_announcements_table_rows:
            element_dict = {}
            element_dict["date"] = row.select("td")[0].get_text().strip()
            element_dict["title"] = fixja.convet_to_half_width(row.select(
                "td")[1].select("div > a")[0].get_text()).strip()
            element_dict["from"] = row.select(
                "td")[2].get_text().strip()
            other_announcements.append(element_dict)

        base.debug_print(
            "[nobo][{}] Other announcements got.".format(self.username))

        return other_announcements

    def get_all_announcements(self):
        if not self.login():
            base.debug_print(
                "[nobo][{}] Error: Login process is failed.".format(self.username))
            return

        base.debug_print(
            "[nobo][{}] Login successful, start to get all announcements.".format(self.username))

        self.webdriver.get(
            self.config["manaba"]["homepage"]+"_announcement")

        page_source = self.webdriver.page_source

        self.webdriver.close()

        return {"emergency": self.get_emergency_announcements(page_source),
                "individual": self.get_announcements_to_individual(page_source),
                "other": self.get_other_announcements(page_source)}
