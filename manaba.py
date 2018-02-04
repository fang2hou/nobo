# -*- coding: utf-8 -*-
# Manaba module of nobo (RitsFun API).
# env: python3
import requests
from bs4 import BeautifulSoup as bs

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

        for row in coursePageCourseTable.select(".courselist-c")[1:-2]:
            print(row.select(".courselist-title")[0].get_text())

        # with open("temp.html", encoding='utf-8', mode='w+') as tempFile:
        #   tempFile.write(str(courseList))
        #   tempFile.close()

    def loadCoursePage(self):
        print(self.webSession.get("https://ct.ritsumei.ac.jp/ct/course_1436639_news_1785319").text)