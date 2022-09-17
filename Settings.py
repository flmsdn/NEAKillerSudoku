import imp

import os
import sys
import json

class SettingsManager():
    def __init__(self):
        self.__path = sys.path[0]+"\\Resources\\config\\settings.json"
        self.loadSettingsFile()
    
    def loadSettingsFile(self):
        folder = self.__path[:-14]
        if "settings.json" not in os.listdir(folder):
            self.__createSettingsFile() #if the file doesn't exist, create it
        with open(self.__path,"r") as file:
            self.__config = json.load(file)
        #check if all fields exist in the settings file
        k = self.__config.keys()
        incompleteConfigFile = False
        if not "AccountName" in k:
            self.__config["AccountName"] = None
            self.__config["Hash"] = None
            incompleteConfigFile = True
        if incompleteConfigFile:
            self.saveSettings() #if any new fields needed to be added, update the settings file as soon as possible
    
    def __createSettingsFile(self):
        with open(self.__path,"w") as file:
            self.__config = {"AccountName":None,"Hash":None}
            file.write(json.dumps(self.__config,separators=(",",":")))

    def getAccount(self):
        return (self.__config["AccountName"],self.__config["Hash"])

    def updateAccount(self,username,hash):
        self.__config["AccountName"] = username
        self.__config["Hash"] = hash
        self.saveSettings()

    def saveSettings(self):
        with open(self.__path,"w") as saveFile:
            saveFile.write(json.dumps(self.__config,separators=(",",":")))