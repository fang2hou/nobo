# -*- coding: utf-8 -*-
# Nobo, a third-party Ritsumeikan API
# 
# lib/base.py
#
# The library including some useful functions.
# -------------------------------------------
# @Author  : Fang2hou
# @Updated : 7/31/2018
# @Homepage: https://github.com/fang2hou/Nobo
# -------------------------------------------
import os
import sys
import json
import hashlib

DEBUG = True

def load_config(path=None):
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
		"cache_dir": "localdb",
		"manaba": {
			"cookies_cache": True,
			"encryption": "md5",
			"sava_mode": "file"
		}
	}

	if None != path:
		with open(path, 'r') as configuration:
			return json.loads(configuration.read())
	
	return default_config

def LoadCookiesFromFile(cacheDirectory, fileId):
	if not os.path.isdir(cacheDirectory + "/cookies/"):
		os.makedirs(cacheDirectory + "/cookies/")

	try:
		with open(cacheDirectory + "/cookies/" + fileId, 'r+') as f:
			return json.loads(f.read())
	except FileNotFoundError:
		return None

def convert_to_md5(str):
	hashlib.md5().update(str.encode("utf8"))
	return hashlib.md5().hexdigest()

def debug_print(str):
	if DEBUG:
		print(str)