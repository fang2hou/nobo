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
import json
import hashlib

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

def export_dict_as_json(path, content):
	"""
	Export data in a dictionary type variable as JSON format.

	Args:
		path: the location of output file.
		content: a dict type variable

	Returns:
		The result of saving.
	"""

	if type(content) != dict:
		print("Error: [Export Dict as JSON] The given data is not a dictionary.")
	return False

	with open(path, 'w+', encoding='utf8') as outfile:
		file_accessed = True
		json.dump(content, outfile, ensure_ascii=False, indent=4)

	if file_accessed:
		return True
	else:
		print("Error: [Export Dict as JSON] Cannot access the file.")
		return False