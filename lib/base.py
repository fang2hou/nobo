import json
import hashlib

def MD5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    print(m.hexdigest())
    return m.hexdigest()

def ExportAsJson(path, content):
	with open(path, 'w+', encoding='utf8') as outfile:
			# Fix Kanji issue, set indent as 4
			json.dump(content, outfile, ensure_ascii=False, indent=4)