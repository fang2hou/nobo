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

def LoadConfiguration(path=None):
	"""Load configration from file.
		
	The configration should be a valid json file.
	If you do not give the path, Nobo will load default configration.

	Args:
		path: the location that configration file is. 
				
	Returns:
		A dict mapping keys to the corresponding table row data
		fetched. 
	"""
	defaultConfig = {
		"cacheDirectory": "localdb",
		"manaba": {
			"cookiesCache": True,
			"encryption": "md5",
			"saveMode": "file"
		}
	}

	if None != path:
		with open(path, 'r') as f:
			return json.loads(f.read())
	else:
		return defaultConfig

def LoadCookiesFromFile(cacheDirectory, fileId):
	if not os.path.isdir(cacheDirectory + "/cookies/"):
		os.makedirs(cacheDirectory + "/cookies/")

	try:
		with open(cacheDirectory + "/cookies/" + fileId, 'r+') as f:
			return json.loads(f.read())
	except FileNotFoundError:
		return None

def ConvertToMd5(str):
	hashlib.md5().update(str.encode("utf8"))
	print(hashlib.md5().hexdigest())
	return hashlib.md5().hexdigest()

def export_json(path, content):
	with open(path, 'w+', encoding='utf8') as outfile:
		json.dump(content, outfile, ensure_ascii=False, indent=4)