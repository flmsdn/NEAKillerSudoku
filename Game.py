import os, sys
import json
import numpy as np

class Game():
    def __init__(self,file=None):
        self.__gameType = 0 #0 is for regular sudoku, 1 is for killer
        self.__gameFile = ""
        self.__fixedCells = []
        if file:
            self.loadGame(file)
        else:
            self.loadGame()
    
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
            for i in range(9):
                for j in range(9):
                    if self.__grid[j][i] != 0:
                        self.__fixedCells.append( [i,j] )
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

    def checkComplete(self):
        npBoard = np.array(self.__grid) #get a numpy 2D array of the grid
        gridRows = [npBoard[i,:] for i in range(9)] #get all of the grid rows
        gridCols = [npBoard[:,j] for j in range(9)] #get all of the grid columns
        gridNonets = [npBoard[i:i+3,j:j+3].flatten() for i in [0,3,6] for j in [0,3,6]] #get all of the nonets in the grid
        for line in np.vstack( [gridRows, gridCols, gridNonets] ): #put all of these groups together and iterate over them
            if len(np.unique(line))<9:
                return False
        return True

if __name__ == "__main__":
    g = Game()
    g.deleteGame("Game1.json")