# -*- coding: utf-8 -*-
# -------------------------------------------
# nobo, No Borders
#
# io.py
# A collection of i/o operation functions.
# -------------------------------------------
# @Author  : Zhou Fang
# @Updated : 1/29/2019
# @Homepage: https://github.com/fang2hou/nobo
# -------------------------------------------
import json
from typing import Any, Dict


def export_as_json(path: str, content: Dict[str, Any]) -> bool:
    """
    Export data as JSON format.

    Args:
            path: the location of output file.
            content: a dict type variable

    Returns:
            The result of saving.
    """
    file_accessed = False

    with open(path, "w+", encoding="utf8") as outfile:
        file_accessed = True
        json.dump(content, outfile, ensure_ascii=False, indent=4)

    if file_accessed:
        return True
    else:
        print("[nobo.io][Export as JSON] Error: Cannot access the file.")
        return False
