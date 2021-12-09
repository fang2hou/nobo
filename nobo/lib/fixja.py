# -*- coding: utf-8 -*-
# -------------------------------------------
# nobo, No Borders
#
# fixja.py
# A collection of Japanese character issue fixing functions.
# -------------------------------------------
# @Author  : Zhou Fang
# @Updated : 1/28/2019
# @Homepage: https://github.com/fang2hou/nobo
# -------------------------------------------


def convet_to_half_width(inputString: str) -> str:
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


def remove_newline(inputString: str) -> str:
    finalString = inputString.replace("\n", "")
    return finalString


def translate_weekday(s: str) -> str:
    convert_dict = {
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

    for jp, en in convert_dict.items():
        s = s.replace(jp, en)

    return s


def remove_last_space(s: str) -> str:
    remove_list = ["\xa0", "\n", "\t", " "]  # Full-width Space used in Japanese

    if s in remove_list:
        s = ""
    else:
        while s[-1:] in remove_list:
            s = s[:-1]

    return s
