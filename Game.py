import os, sys
import json
import numpy as np
from GridGeneration import Generator

class Game():
    def __init__(self,file=None):
        self.__gameType = 0 #0 is for regular sudoku, 1 is for killer
        self.__gameFile = ""
        self.__fixedCells = []
        self.__gen = Generator()

    def getFile(self):
        return self.__gameFile
    
    def __getFixedCells(self):
        for i in range(9):
            for j in range(9):
                if self.__grid[j][i] != 0:
                    self.__fixedCells.append( [i,j] )

    def solve(self):
        self.__grid = self.__gen.solveGrid(self.__grid)

    def newGame(self, difficulty):
        self.__gameFile = ""
        self.__gameType = 0
        self.__fixedCells = []
        self.__grid = self.__gen.genGrid(difficulty)
        self.__getFixedCells()

    def saveGame(self,file):
        if file==".json":
            return False
        filePath = "\\LocalGames\\"+file
        gameObject = {}
        gameObject["gameType"] = self.__gameType
        gameObject["board"] = self.__grid
        gameObject["fixedCells"] = self.__fixedCells
        saveFile = open(sys.path[0]+filePath,"w")
        saveFile.write(json.dumps(gameObject,separators=(",",":")))
        saveFile.close()

    def loadGame(self,file="DefaultGame.json"):
        if not file: file="DefaultGame.json"
        self.__gameFile = file
        filePath = "\\LocalGames\\"+file
        loadFile = open(sys.path[0]+filePath,"r")
        gameObject = json.load(loadFile)
        loadFile.close()
        self.__gameType = gameObject["gameType"]
        self.__grid = gameObject["board"]
        try:
            self.__fixedCells = gameObject["fixedCells"]
            print(self.__fixedCells)
        except:
            self.__getFixedCells()
            self.saveGame(file)
            print(self.__fixedCells)

    def deleteGame(self,file=None):
        if not file:
            file = self.__gameFile
        filePath = "\\LocalGames\\"+file
        try:
            os.remove(sys.path[0]+filePath)
            return True
        except:
            return False

    def getType(self):
        return self.__gameType

    def getGrid(self):
        return self.__grid
    
    def getCell(self,x,y):
        return self.__grid[y][x]

    def updateCell(self,x,y, value):
        self.__grid[y][x] = value
    
    def checkCell(self,x,y):
        return not [x,y] in self.__fixedCells

    def checkFull(self):
        return not 0 in np.array(self.__grid)

    def checkComplete(self, grid=None):
        if grid is None:
            grid = self.__grid
        return self.__gen.checkComplete(grid)

if __name__ == "__main__":
    g = Game()
    g.deleteGame("Game1.json")