#!/usr/bin/python3
# ##########################################################
# Script for creating backups and uploading to Dropbox     #
# ##########################################################

import os.path
import re
import sys
import time
import socket
import getpass
import glob

# Global variables
appDropboxUploader = '/opt/dropbox-uploader/dropbox_uploader.sh'
varScriptDir = os.path.dirname(os.path.realpath(__file__))
varStatus = '/tmp/backup_status.txt'
varHostname = socket.gethostname()

def loadConfig(pathConfig):
	if os.path.isfile(pathConfig) == False:
		raise ValueError("Config file is unreadable", pathConfig)

	configFile = open(pathConfig, 'r').read()

	taskName = ''
	taskPassword = ''
	taskPaths = []
	taskEnabled = False
	taskExecBefore = ''
	taskExecAfter = ''

	enabledRx = re.search("@ENABLED=([^\t\s\r\n]+)", configFile)

	if enabledRx:
		taskEnabled = bool(enabledRx.group(1) == "1")
	else:
		raise ValueError("Task status is not defined")

	taskRx = re.search("@TASK=([^\t\s\r\n]+)", configFile)

	if taskRx:
		taskName = taskRx.group(1)
	else:
		raise ValueError("Task name is not defined")

	if len(taskName) == 0:
		raise ValueError("Task name is empty")

	passwordRx = re.search("@PASSWORD=([^\t\s\r\n]+)", configFile)

	if passwordRx:
		taskPassword = passwordRx.group(1)
	else:
		raise ValueError("Password is not defined")

	if len(taskPassword) == 0:
		raise ValueError("Password is empty")

	pathsRx = re.search("@PATHS\n(.*)", configFile, re.M)

	if pathsRx:
		tmp = configFile[pathsRx.start(1):].split('\n')
		taskPaths = [elem for elem in tmp if len(elem) > 0]
	else:
		raise ValueError("Paths are not defined")

	if len(taskPaths) == 0:
		raise ValueError("Paths list is empty")

	execBeforeRx = re.search("@EXECBEFORE=([^\t\s\r\n]+)", configFile)

	if execBeforeRx:
		taskExecBefore = (execBeforeRx.group(1)).replace('\n', ' ').strip()

	execAfterRx = re.search("@EXECAFTER=([^\t\s\r\n]+)", configFile)

	if execAfterRx:
		taskExecAfter = (execAfterRx.group(1)).replace('\n', ' ').strip()

	return {
		'name'       : taskName,
		'password'   : taskPassword,
		'paths'      : taskPaths,
		'enabled'    : taskEnabled,
		'execbefore' : taskExecBefore,
		'execafter'  : taskExecAfter
	}
# / loadConfig

def isRoot():
	username = getpass.getuser()

	return username == "root"
# / isRoot

def fileWrite(file, text):
	outfile = open(file, 'w')
	outfile.write(str(text))
	outfile.write("\n")
	outfile.close()
# / fileWrite

def fileAppend(file, text):
	outfile = open(file, 'a')
	outfile.write(str(text))
	outfile.write("\n")
	outfile.close()
# / fileWrite

def createBackup(task):
	# Script variables
	varToday = time.strftime("%Y%m%d", time.gmtime())
	varTimestamp = int(time.time())

	# Backup variables
	bkpTask = task['name']
	bkpPassword = task['password']
	appDropboxPath = '/{0}/{1}'.format(varHostname, bkpTask)
	bkpName = '{0}_backup_{1}.tar.gz.gpg'.format(bkpTask, varToday)
	bkpTarget = '/tmp/{0}'.format(bkpName)
	bkpPaths = '{0}-paths.txt'.format(bkpTarget)

	# Checking for root
	if isRoot() == False:
		raise ValueError("Script has to work under 'root' user")

	print ("* Starting backup for task:", task['name'])

	# Writing paths list to file
	fileWrite(bkpPaths, '\n'.join(task['paths']))

	# Pre-check completed
	print ("> Pre-check completed")
	print ("  Task: {0}".format(bkpTask))
	print ("  Target: {0}".format(bkpTarget))
	print ("  Backup paths:", task['paths'])

	# Writing status file
	print ("> Starting backup")
	fileWrite(varStatus, bkpTask)
	fileAppend(varStatus, varTimestamp)

	# Check if backup file already exists, if yes -> skip
	if os.path.isfile(bkpTarget) == False:
		# Exec pre-backup script
		if task['execbefore'] != '':
			print ("> Executing pre-backup script")
			os.system(task['execbefore'])

		# Creating backup
		cmd = (\
			'/bin/tar -f - -c -z --files-from={0} | ' + \
			'/usr/bin/gpg --symmetric --yes --passphrase {1} --compress-algo 0 --cipher-algo AES256 --no-tty --batch ' + \
			'> {2}').format(
				bkpPaths,
				bkpPassword,
				bkpTarget
			).replace('\n', ' ').strip()

		os.system(cmd)
	else:
		print ("NOTICE: backup target archive already exists, skipping...")

	# Backup should exists as of now
	if os.path.isfile(bkpTarget) == False:
		raise ValueError("Backup target is not available, possibly backup creation failed")

	print ("> Uploading")
	os.system('{0} delete {1}'.format(appDropboxUploader, appDropboxPath))
	os.system('{0} mkdir {1}'.format(appDropboxUploader, appDropboxPath))
	os.system('{0} upload {1} {2}/{3}'.format(appDropboxUploader, bkpTarget, appDropboxPath, bkpName))

	print ("> Finishing")
	if os.path.isfile(varStatus): os.remove(varStatus) # Removing status file
	if os.path.isfile(bkpTarget): os.remove(bkpTarget) # Removing backup target file
	if os.path.isfile(bkpPaths):  os.remove(bkpPaths)  # Removing paths list file

	if task['execafter'] != '':
		print ("> Executing after-backup script")
		os.system(task['execafter'])
# / createBackup

# Is dropbox-uploader installed?
if os.path.isfile(appDropboxUploader) == False:
	print ("Dropbox Uplaoder is not installed")
	sys.exit(1)

# If started with argument - it's a config name
if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
	print ("NOTICE: Starting single-config mode")
	try:
		configFile = ("{}/tasks/{}.txt").format(
			varScriptDir, sys.argv[1]
		)

		config = loadConfig(configFile)

		if config['enabled'] == True:
			createBackup(config)
		else:
			print ("* Task defined in file '{}' is disabled".format(configFile))
	except ValueError as err:
		print('Exception:', err)
else:
	# Reading config list
	configList = glob.glob(varScriptDir + "/tasks/*.txt")

	for configFile in configList:
		try:
			config = loadConfig(configFile)
			# print (config)

			if config['enabled'] == True:
				createBackup(config)
			else:
				print ("* Task defined in file '{}' is disabled".format(configFile))
		except ValueError as err:
			print ('Exception:', err)
