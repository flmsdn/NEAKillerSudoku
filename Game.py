from collections import Counter
from itertools import product
import os, sys
import json
import numpy as np
from GridGeneration import Generator

# handles the board and interactions with the board
class Game():
    EMPTY = 0
    def __init__(self,file=None):
        self.__gameType = 0 #0 is for regular sudoku, 1 is for killer
        self.__gameFile = ""
        #contains a list of cell coordinates that cannot be edited by the user
        self.__fixedCells = []
        self.__gen = Generator()
        self.__pencilMarkings = [[None for _ in range(9)] for _ in range(9)]
        self.__writeMode = 0 #0 is pen, 1 is pencil

    #returns the current game file name
    def getFile(self):
        return self.__gameFile

    #calculates the fixed cells in the grid
    def __getFixedCells(self):
        for i in range(9):
            for j in range(9):
                if self.__grid[j][i] != self.EMPTY:
                    self.__fixedCells.append( [i,j] )

    def toggleWrite(self):
        self.__writeMode = 0 if self.__writeMode else 1

    #returns the current list of fixed cell coordinates
    def fixedCells(self):
        return self.__fixedCells

    def getErrorCells(self):
        errorCells = set()
        g= np.array(self.__grid)
        rs,cs,ns = [],[],[]
        for i in range(9):
            r = Counter(g[i])
            c = Counter(g[:,i])
            nonet = g[3*(i//3):3*(i//3)+3,3*(i%3):3*(i%3)+3]
            n = Counter(nonet.flatten())
            rs.append(r)
            cs.append(c)
            ns.append(n)
        for i,j in product(range(9),range(9)):
            #check row, col and nonet
            cell = g[j,i]
            if cell==0:
                pass
            elif rs[j][cell]>1 or cs[i][cell]>1 or ns[3*(j//3)+i//3][cell]>1:
                errorCells.add( (i,j) )
        if self.__gameType==1:
            #check if cage sums make sense and check for repetition
            for cage in self.__cages:
                cells = [g[c[1],c[0]] for c in cage.cells]
                vals = [c for c in cells if c >0]
                if sum(cells)>cage.sum or len(set(vals)) != len(vals):
                    for n in cage.cells:
                        errorCells.add( tuple(n) )
        return errorCells

    #solves the current grid
    def solve(self):
        #we cannot just solve the current grid - we have to solve a grid without any user changes
        emptiedGrid = np.zeros((9,9),dtype=int) #make a copy of the grid
        for a in self.__fixedCells:
            emptiedGrid[a[1],a[0]] = self.__grid[a[1]][a[0]]
        #remove all user changes from emptied grid and solve
        if self.__gameType==0:
            self.__grid = self.__gen.solveGrid(emptiedGrid)
        elif self.__gameType==1:
            self.__grid = self.__gen.solveKillerGrid(emptiedGrid,self.__cages)

    def newGame(self, difficulty,gameType=1):
        #reset the game
        self.__gameFile = ""
        self.__gameType = gameType
        self.__errors = 0
        self.__fixedCells = []
        if self.__gameType==0:
            self.__grid = self.__gen.genGrid(difficulty)
        elif self.__gameType==1:
            self.__grid, cageList = self.__gen.genKillerGrid(difficulty)
            self.__cages = self.__gen.getCages(cageList,self.__grid)
            self.__cageDict = self.__gen.getCageDict(self.__cages)
        self.__getFixedCells()

    #saves the current game to memory
    def saveGame(self,file,errors=0):
        if file==".json":
            return False
        filePath = "\\LocalGames\\"+file
        gameObject = {}
        gameObject["gameType"] = self.__gameType
        if type(self.__grid)!=list:
            gameObject["board"] = self.__grid.tolist()
        else:
            gameObject["board"] = self.__grid
        gameObject["markings"] = self.__pencilMarkings
        gameObject["fixedCells"] = self.__fixedCells
        gameObject["errors"] = errors
        if self.__gameType==1:
            gameObject["cages"] = self.__gen.getCageList(self.__cages)
        saveFile = open(sys.path[0]+filePath,"w")
        saveFile.write(json.dumps(gameObject,separators=(",",":")))
        saveFile.close()

    def loadGame(self,file="DefaultGame.json"):
        if not file or file==".json": file="DefaultGame.json"
        self.__gameFile = file
        filePath = "\\LocalGames\\"+file
        loadFile = open(sys.path[0]+filePath,"r")
        gameObject = json.load(loadFile)
        loadFile.close()
        self.__gameType = gameObject["gameType"]
        self.__grid = gameObject["board"]
        if "markings" in gameObject:
            self.__pencilMarkings = gameObject["markings"]
        if self.__gameType==1:
            self.__cages = self.__gen.getCages(gameObject["cages"],self.__grid)
            self.__cageDict = self.__gen.getCageDict(self.__cages)
        try:
            self.__errors = gameObject["errors"]
        except:
            self.__errors = 0
        if "fixedCells" in gameObject:
            self.__fixedCells = gameObject["fixedCells"]
        else:
            self.__getFixedCells()
            self.saveGame(file)

    def deleteGame(self,file=None):
        if not file:
            file = self.__gameFile
        filePath = "\\LocalGames\\"+file
        try:
            os.remove(sys.path[0]+filePath)
            return True
        except:
            return False

    def getErrors(self):
        return self.__errors

    def getType(self):
        return self.__gameType

    def getGrid(self):
        return self.__grid

    def getCages(self):
        return self.__cages

    def getCagesDict(self):
        return self.__cageDict
    
    def getCell(self,x,y):
        return self.__grid[y][x]

    def getPencilMarkings(self):
        return self.__pencilMarkings

    def updateCell(self,x,y, value, writeMode=None):
        if writeMode==None:
            writeMode = self.__writeMode
        if writeMode == 0:
            self.__grid[y][x] = value
            if type(self.__pencilMarkings[y][x])==list:
                self.__pencilMarkings[y][x] = None
            nonetx,nonety = (x//3)*3,(y//3)*3
            for a in range(9):
                nx,ny=nonetx+a%3,nonety+a//3
                if not nx == x and not ny==y:
                    if type(self.__pencilMarkings[ny][nx])==list:
                        if value in self.__pencilMarkings[ny][nx]:
                            self.__pencilMarkings[ny][nx].remove(value)
                if a!=y:
                    if type(self.__pencilMarkings[a][x])==list:
                        if value in self.__pencilMarkings[a][x]:
                            self.__pencilMarkings[a][x].remove(value)
                if a!=x:
                    if type(self.__pencilMarkings[y][a])==list:
                        if value in self.__pencilMarkings[y][a]:
                            self.__pencilMarkings[y][a].remove(value)
        else:
            if self.__grid[y][x]!=0: return
            if type(self.__pencilMarkings[y][x])==list:
                if value in self.__pencilMarkings[y][x]:
                    self.__pencilMarkings[y][x].remove(value)
                else:
                    self.__pencilMarkings[y][x].append(value)
            else:
                self.__pencilMarkings[y][x] = [value]
    
    def checkCell(self,x,y):
        return not [x,y] in self.__fixedCells

    def checkFull(self):
        return not  self.EMPTY in np.array(self.__grid)

    def checkComplete(self, grid=None):
        if grid is None:
            grid = self.__grid
        return self.__gen.checkComplete(grid)

if __name__ == "__main__":
    g = Game()
    g.deleteGame("Game1.json")