# -*- coding: utf-8 -*-
# fixJapanese module of nobo (RitsFun API).
# env: python3
def convertHalfwidth(inputString):
	fixDict = {
		"　": " ",
		"１": "1",
		"２": "2",
		"３": "3",
		"４": "4",
		"５": "5",
		"６": "6",
		"７": "7",
		"８": "8",
		"９": "9",
		"０": "0",
		"（": "(",
		"）": ")",
	}
	finalString = inputString
	for full, half in fixDict.items():
		finalString = finalString.replace(full, half)
	return finalString

def removeNewLine(inputString):
	finalString = inputString.replace("\n", "")
	return finalString

def convertWeekday(inputString):
	convertDict = {
		"月": "Monday",
		"火": "Tuesday",
		"水": "Wednesday",
		"木": "Thursday",
		"金": "Friday",
		"月曜": "Monday",
		"火曜": "Tuesday",
		"水曜": "Wednesday",
		"木曜": "Thursday",
		"金曜": "Friday",
		"月曜日": "Monday",
		"火曜日": "Tuesday",
		"水曜日": "Wednesday",
		"木曜日": "Thursday",
		"金曜日": "Friday",
	}
	finalString = inputString
	for jaweek, enweek in convertDict.items():
		finalString = finalString.replace(jaweek, enweek)

	return finalString

def removeLast(inputString):
	finalString = inputString

	removeList = [
		"\xa0",
		"\n",
		"\t",
		" "
	]

	if (finalString in removeList):
		finalString = ""
	else:
		while (finalString[-1:] in removeList):
		 	finalString = finalString[:-1]

	return finalString