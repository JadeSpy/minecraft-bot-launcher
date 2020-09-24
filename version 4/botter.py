import os 
import time
import minecraft_launcher_lib
import subprocess
import logging
import threading
import keyboard
import random
crashesCount = 0
shouldTerminate = False
def processList(): #Returns All processes in a list
	output = os.popen('wmic process get description, processid').read()
	val = output.split("\n")
	newList = []
	for part in val:
		if(part!=""):
			replace = ""
			found=False
			finalPart = ""
			for char in part:
				if(char==" " and found!=True):
					found = True
					finalPart += ","
				elif(char==" "):
					pass
				else:
					finalPart+=char

			newList.append(finalPart)
	return(newList)
def processDifferences(pros1, pros2): #find values that occur in process list 1 and not process list 2
	returnVals = []
	for i in pros1:
		if("javaw" in i):
			if(i not in pros2):
				returnVals.append(i)
	return(returnVals)
def waitForLaunch(email):
	baseline = processList()
	#launch minecraft
	while True:
		isOpenTest = processList()
		result = processDifferences(isOpenTest, baseline) #sees if new minecraft has appeared
		if(len(result) == 1):
			identifier = result[0].split(",")
			return(email + "," +identifier[1])
		if(len(result) > 1):
			print("Error, multiple new minecraft windows!")
			return(False)
		time.sleep(1)
def closeAll(process, delay):
	global crashesCount
	pL=processList()
	for i in pL:
		if(process in i):
			ident = i.split(",")
			print(ident)
			os.kill(int(ident[1]), 9)
			time.sleep(delay)
			crashesCount = crashesCount-1
def killMinecraftNotResponding():
	name1 = "javaw.exe"
	name2 = "java.exe"
	notRespondingTracker = []
	while True:
		for i in range (0, 1200):
			if(shouldTerminate == True):
				return
			time.sleep(0.25)
		try:
			r = os.popen('tasklist /v').read().strip().split('\n')
			while len(notRespondingTracker)>30:
				notRespondingTracker.pop(0)
			for i in range(len(r)):
				s = r[i]
				if((name1 in r[i].lower() or name2 in r[i].lower()) and "responding" in r[i].lower()):
					stripped = r[i].split()
					identifier = int(stripped[1])

					print("Killed a non-responding window!")
					print("stripped: ", stripped)
					os.kill(identifier, 9)
		except Exception as e:
			for i in range (0, 100):
				print(e)
			

def getForge():
	path = minecraft_launcher_lib.utils.get_minecraft_directory()
	versions = minecraft_launcher_lib.utils.get_installed_versions(path)
	for i in versions:
		check = i["id"]
		if("1.12.2" in check):
			if "forge" in check:
				return(check)
	return(False)
def launchAccount(email, password):
	global crashesCount
	global shouldTerminate
	global version
	minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
	#minecraft_launcher_lib.install.install_minecraft_version(version,minecraft_directory)
	while True:
		try:
			login_data = minecraft_launcher_lib.account.login_user(email,password)
			try:
				options = {
			    "username": login_data["selectedProfile"]["name"],
			    "uuid": login_data["selectedProfile"]["id"],
			    "token": login_data["accessToken"]
			}
			except:
				print("Bad password and/or email address")
				return(False)
			minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(version,minecraft_directory,options)
			subprocess.call(minecraft_command)
			crashesCount=crashesCount+1
			f = open("crashCount.txt", 'w')
			f.write("Current crashes:")
			f.write(str(crashesCount))
			f.close()
			if(shouldTerminate == True):
				return
		except Exception as e:
			print(e)
			print(crashesCount)
			f = open("crashCount.txt", 'w')
			f.write(str(crashesCount))
			f.close()
		if(shouldTerminate == True):
			return
		for i in range(100):
			if(shouldTerminate == True):
				return
			time.sleep(0.1)
def runAlts(name, password):
	while True:
		try:
			print(name, "is launching")
			loginSuccessful = launchAccount(name, password)
		except Exception as e: 
			print(e)
			print("error launching:", name)

		if(shouldTerminate == True):
			return
def readAccounts():
	global shouldTerminate

	if not os.path.isfile('BotAccounts.txt'):
		createFile = open('BotAccounts.txt', 'w+')
		createFile.write("email@domain.com:password\nemail2@domain2.com:password2")
		createFile.close()
	with open("BotAccounts.txt") as fp:
		line = fp.readline()
		threadList = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		count = -1
		while line:
			count =count+1
			line = line.strip()
			accountAsList = line.split(":")
			line = fp.readline()
			threadList[count] = threading.Thread(target=runAlts, args=(accountAsList[0],accountAsList[1]))
			threadList[count].start()
			for i in range(0,240):
				if(shouldTerminate==True): 
					return()
				time.sleep(0.25)
def keyListener():
	global shouldTerminate
	if(shouldTerminate==True):
		return
	while True:
		time.sleep(0.05)
		if keyboard.is_pressed('q') and keyboard.is_pressed('u'):  # if key 'q' is pressed 
			shouldTerminate = True
			closeAll("java", 1)
			print("canceling...")
			return()  # finishing the loopqu
		#except:
		#	break
def periodicalRestart():
	global shouldTerminate
	restartSeconds = 3600 #1 hours
	while True:
		restartSeconds = random.uniform(5000, 10800)
		#restartSeconds = 30
		for i in range (0, round(restartSeconds*4)):
			if(shouldTerminate==True): 
				return()
			time.sleep(0.25)
		print("Restarting")
		closeAll("java", 120)
version = getForge()

keyListenerThread = threading.Thread(target=keyListener)
keyListenerThread.start()
periodicalRestartThread = threading.Thread(target=periodicalRestart)
periodicalRestartThread.start()
killNoRespond = threading.Thread(target=killMinecraftNotResponding)
killNoRespond.start()
readAccounts()














