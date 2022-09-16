import imp


import sys
import json

class Settings():
    def __init__(self):
        self.__path = sys.path[0]+"\\Resources\\config\\settings.json"
        self.__loadSettingsFile()
    
    def __loadSettingsFile(self):
        self.__config = json.load(self.__path)
        #check if all fields exist in the settings file
        k = self.__config.keys()
        if not "AccountName" in k:
            self.__config["AccountName"] = None
            self.__config["Hash"] = None
    
    def getAccount(self):
        return (self.__config["AccountName"],self.__config["Hash"])
    
    def saveSettings(self):
        saveFile = open(self.__path,"w")
        saveFile.write(json.dumps(self.__config,separators=(",",":")))