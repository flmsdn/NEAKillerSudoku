import os
import sys

class Game():
    def __init__(self):
        self.__gameType = 0 #0 is for regular sudoku, 1 is for killer
        self.loadGame()
    
    def loadGame(self,file="DefaultGame.txt"):
        loadFile = open(os.path.join(sys.path[0],file),"r")
        self.__grid = [[0,0,0,0,6,0,0,0,0],[0,0,0,4,0,3,6,7,0],[0,0,5,0,0,7,0,0,0],[0,9,0,0,0,0,4,0,0],[1,0,0,0,0,0,9,0,3],[0,3,2,0,0,0,0,5,8],[0,1,0,5,2,0,0,9,7],[0,5,0,0,0,9,8,0,0],[0,0,0,0,8,6,2,0,0]]

    def getType(self):
        return self.__gameType

    def getGrid(self):
        return self.__grid

    def updateCell(self,x,y, value):
        self.__grid[y][x] = value