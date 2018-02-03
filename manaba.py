import requests

myUsername = "is0000ab"
myPassword = "12345678"
myPagePath = "https://ct.ritsumei.ac.jp/ct/home"

webSession = requests.Session()

def getValueFromHTML(name, page):
    pageText = page.text
    try:
        tempPageData = pageText.split(name + " value=\"")[1]
    except:
        tempPageData = pageText.split(name + "\" value=\"")[1]
    resultValue = tempPageData.split("\"")[0]
    return resultValue

def getActionFromHTML(method, page):
    try:
        tempPageData = page.text.split("METHOD=\"" + method + "\" ACTION=\"")[1]
        resultAction = tempPageData.split("\">")[0]
    except:
        tempPageData = page.text.split("<form action=\"")[1]
        resultAction = tempPageData.split("\"")[0]
    return resultAction

# 1
firstPage = webSession.get(myPagePath)

postFormDataPage1 = {
    "USER": myUsername,
    "PASSWORD": myPassword,
    "target": getValueFromHTML("target", firstPage),
    "smauthreason": getValueFromHTML("smauthreason", firstPage),
    "smquerydata": getValueFromHTML("smquerydata", firstPage),
    "postpreservationdata": getValueFromHTML("postpreservationdata", firstPage),
}

# 2
secondPage = webSession.post("https://sso.ritsumei.ac.jp/cgi-bin/pwexpcheck.cgi", postFormDataPage1)

actionPage = getActionFromHTML("POST", secondPage)

postFormDataPage2 = {
    "USER": postFormDataPage1["USER"],
    "PASSWORD": postFormDataPage1["PASSWORD"],
    "smquerydata": postFormDataPage1["smquerydata"],
}

# 3
thirdPage = webSession.post("https://sso.ritsumei.ac.jp" + actionPage, postFormDataPage2)


postFormDataPage3 = {
    "RelayState": getValueFromHTML("RelayState", thirdPage).replace("&#x3a;",":").replace("&#x2f;","/"),
    "SAMLResponse": getValueFromHTML("SAMLResponse", thirdPage),
}

actionPage = getActionFromHTML("POST", thirdPage).replace("&#x3a;",":").replace("&#x2f;","/")

forthPage = webSession.post(actionPage, postFormDataPage3)



# ----------------------------
# For debug

with open("D:/temp.html", encoding='utf-8', mode='w+') as tempFile:
    tempFile.write(forthPage.text)
    tempFile.close()

# print(webSession.cookies)
# print(firstPage.text)
# print(secondPage.text)
# print(thirdPage.text)
# print(forthPage.text)
