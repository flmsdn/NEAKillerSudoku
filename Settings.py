import os
import sys
import json

class SettingsManager():
    def __init__(self):
        self.__path = sys.path[0]+"\\Resources\\config\\settings.json"
        self.loadSettingsFile()

    def getTheme(self,ind):
        folder = [k for k in os.listdir(self.__path[:-14]) if "Theme" in k]
        with open(self.__path[:-14]+"\\"+folder[ind],"r") as file:
            theme = json.load(file)
        for k in theme.keys():
            theme[k] = tuple(theme[k])
        return theme

    def getThemes(self):
        folder = self.__path[:-14]
        return [k for k in os.listdir(folder) if "Theme" in k]

    def setTheme(self,ind):
        folder = self.__path[:-14]
        themeFiles =  [k for k in os.listdir(folder) if "Theme" in k]
        if not 0<=ind<len(themeFiles): return
        self.__config["Theme"] = ind
        self.__saveSettings()

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
            self.__saveSettings() #if any new fields needed to be added, update the settings file as soon as possible
    
    def __createSettingsFile(self):
        with open(self.__path,"w") as file:
            self.__config = {"AccountName":None,"Hash":None, "Theme":3, "Audio":"classic", "Muted": False}
            file.write(json.dumps(self.__config,separators=(",",":")))

    def getAccount(self):
        return (self.__config["AccountName"],self.__config["Hash"])

    def getConfigTheme(self):
        return self.__config["Theme"]

    def getConfigAudio(self):
        return self.__config["Audio"]
    
    def setAudio(self,audio):
        self.__config["Audio"] = audio
        self.__saveSettings()
    
    def toggleMute(self):
        self.__config["Muted"] = not self.__config["Muted"]
        self.__saveSettings()
    
    def getMuted(self):
        return self.__config["Muted"]

    def updateAccount(self,username,hash):
        self.__config["AccountName"] = username
        self.__config["Hash"] = hash
        self.__saveSettings()

    def __saveSettings(self):
        with open(self.__path,"w") as saveFile:
            saveFile.write(json.dumps(self.__config,separators=(",",":")))