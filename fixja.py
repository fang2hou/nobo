# -*- coding: utf-8 -*-
# Nobo, a third-party Ritsumeikan API
#
# lib/fixja.py
#
# The library for fixing some Japanese issue.
# -------------------------------------------
# @Author  : Fang2hou
# @Updated : 7/31/2018
# @Homepage: https://github.com/fang2hou/Nobo
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


def remove_newline(inputString):
    finalString = inputString.replace("\n", "")
    return finalString


def translate_weekday(string):
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
        string = string.replace(jp, en)

    return string


def remove_last_space(string):
    remove_list = [
        "\xa0",  # Full-width Space used in Japanese
        "\n",
        "\t",
        " "
    ]

    if string in remove_list:
        string = ""
    else:
        while string[-1:] in remove_list:
            string = string[:-1]

    return string
