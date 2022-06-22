import sys
import json
import numpy as np

class Game():
    def __init__(self,file=None):
        self.__gameType = 0 #0 is for regular sudoku, 1 is for killer
        if file:
            self.loadGame(file)
        else:
            self.loadGame()
    
    def loadGame(self,file="DefaultGame.json"):
        filePath = "\\LocalGames\\"+file
        loadFile = open(sys.path[0]+filePath,"r")
        gameObject = json.load(loadFile)
        self.__gameType = gameObject["gameType"]
        self.__grid = gameObject["board"]

    def getType(self):
        return self.__gameType

    def getGrid(self):
        return self.__grid

    def updateCell(self,x,y, value):
        self.__grid[y][x] = value
    
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
    if 0 in np.array(g.getGrid()): print(True)