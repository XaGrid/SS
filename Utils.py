import os

FilePath = "C:\\SSF"

try:
	os.mkdir(FilePath)
except:
	pass

def resource_path(file):
	return os.path.join(FilePath , file)

def check_file(file):
	return os.path.isfile(FilePath + "\\" + file)