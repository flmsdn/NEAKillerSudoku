import itertools
import random
import numpy as np

class Generator():
    def __init__(self):
        self.__nums = list(range(1,10))
        self.__count = 0

    def checkComplete(self, grid):
        npBoard = np.array(grid) #get a numpy 2D array of the grid
        gridRows = [npBoard[i,:] for i in range(9)] #get all of the grid rows
        gridCols = [npBoard[:,j] for j in range(9)] #get all of the grid columns
        gridNonets = [npBoard[i:i+3,j:j+3].flatten() for i in [0,3,6] for j in [0,3,6]] #get all of the nonets in the grid
        for line in np.vstack( [gridRows, gridCols, gridNonets] ): #put all of these groups together and iterate over them
            if len(np.unique(line))<9:
                return False
        return True

    #logic from https://www.101computing.net/sudoku-generator-algorithm/
    def fillGrid(self,grid):
        for row, col in itertools.product(range(9),range(9)):
            if grid[row][col]==0:
                random.shuffle(self.__nums)
                for num in self.__nums:
                    if not num in grid[row,:]:
                        if not num in grid[:,col]:
                            nonetX, nonetY = col//3, row//3
                            nonet = grid[nonetY*3:nonetY*3+3,nonetX*3:nonetX*3+3].flatten()
                            if not num in nonet:
                                grid[row][col] = num
                                if 0 in grid:
                                    if self.fillGrid(grid):
                                        return True
                                else:
                                    return True
                break
        grid[row][col]=0
    
    def iterateGrid(self,grid,saveState):
        #iterate over all cells
        for row, col in itertools.product(range(9),range(9)):
            if grid[row][col]==0:
                #if the value is 0, iterate over all possible values
                for num in range(1,10):
                    if not num in grid[row,:]:
                        if not num in grid[:,col]:
                            nonetX, nonetY = col//3, row//3
                            nonet = grid[nonetY*3:nonetY*3+3,nonetX*3:nonetX*3+3].flatten()
                            if not num in nonet:
                                grid[row][col] = num
                                if 0 in grid:
                                    if self.iterateGrid(grid,saveState):
                                        return True
                                else:
                                    self.__count+=1
                                    if saveState:
                                        grid[row, col] = num
                                    break
                break
        if not saveState:
            grid[row, col]=0
    
    def solveGrid(self,grid):
        while True:
            gridTrial = np.copy(grid)
            self.fillGrid(gridTrial)
            if self.checkComplete(gridTrial):
                return gridTrial
    
    def genGrid(self, difficulty):
        grid = np.array([[0]*9]*9,ndmin=2) #empty grid
        self.fillGrid(grid) #fill grid in with random values
        #limit difficulty
        if difficulty>7: difficulty=7
        elif difficulty<1: difficulty=1
        while difficulty:
            '''
            while True:
                r,c = random.choice(range(9)),random.choice(range(9))
                if grid[r,c]: break'''
            zeros = list(zip(*np.where(grid>0)))
            r,c = random.choice(zeros)
            oldVal = grid[r,c]
            grid[r,c]=0
            #copy grid so no permanent change are made
            gridCopy = np.copy(grid)
            self.__count=0
            self.iterateGrid(gridCopy,False)
            if self.__count!=1:
                grid[r,c]=oldVal
                difficulty-=1
        return grid

if __name__ == "__main__":
    g = Generator()
    grid = g.genGrid(1)
    print(grid)
    solved = g.solveGrid(grid)
    print(solved)