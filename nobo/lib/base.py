# -*- coding: utf-8 -*-
# -------------------------------------------
# nobo, No Borders
#
# fixja.py
# A collection of useful basic functions.
# -------------------------------------------
# @Author  : Zhou Fang
# @Updated : 1/28/2019
# @Homepage: https://github.com/fang2hou/nobo
# -------------------------------------------
import hashlib
import json
import os
from typing import Any, Dict, Optional

DEBUG = True


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.

    The configuration should be a valid JSON file.
    If the path is empty, Nobo will load default configuration.

    Args:
            path: the location that configuration file is.

    Returns:
            A dict mapping keys to the corresponding table row data fetched.
    """

    default_config = {
        "basic": {"local_cache_dir": "localdb"},
        "manaba": {
            "homepage": "https://ct.ritsumei.ac.jp/ct/home",
            "domain_root": "ct.ritsumei.ac.jp",
            "login_domain_root": "sso.ritsumei.ac.jp",
            "login_attempt_interval": 0.5,
            "timeout": 10,
            "cookies_cache": True,
            "encryption": "md5",
            "save_mode": "file",
        },
    }

    if path is not None:
        with open(path, "r") as configuration:
            return json.loads(configuration.read())

    return default_config


def LoadCookiesFromFile(cacheDirectory: str, fileId: str) -> Optional[Dict[str, Any]]:
    if not os.path.isdir(cacheDirectory + "/cookies/"):
        os.makedirs(cacheDirectory + "/cookies/")

    try:
        with open(cacheDirectory + "/cookies/" + fileId, "r+") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return None


def convert_to_md5(s: str) -> str:
    hashlib.md5().update(s.encode("utf8"))
    return hashlib.md5().hexdigest()


def debug_print(s: object) -> None:
    if DEBUG:
        print(s)
