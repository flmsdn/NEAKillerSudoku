import itertools
import random
import numpy as np

class Generator():
    def __init__(self):
        self.__nums = list(range(1,10))
        self.__count = 0

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
    
    def iterateGrid(self,grid):
        for row, col in itertools.product(range(9),range(9)):
            if grid[row][col]==0:
                for num in range(1,10):
                    if not num in grid[row,:]:
                        if not num in grid[:,col]:
                            nonetX, nonetY = col//3, row//3
                            nonet = grid[nonetY*3:nonetY*3+3,nonetX*3:nonetX*3+3].flatten()
                            if not num in nonet:
                                grid[row][col] = num
                                if 0 in grid:
                                    if self.iterateGrid(grid):
                                        return True
                                else:
                                    self.__count+=1
                                    break
                break
        grid[row][col]=0
    
    def genGrid(self, difficulty):
        grid = np.array([[0]*9]*9,ndmin=2)
        self.fillGrid(grid)
        #limit difficulty
        if difficulty>7: difficulty=7
        elif difficulty<1: difficulty=1
        while difficulty:
            while True:
                r,c = random.choice(range(9)),random.choice(range(9))
                if grid[r,c]: break
            oldVal = grid[r,c]
            grid[r,c]=0
            #copy grid so no permanent change are made
            gridCopy = np.copy(grid)
            self.__count=0
            self.iterateGrid(gridCopy)
            if self.__count!=1:
                grid[r,c]=oldVal
                difficulty-=1
        return grid

if __name__ == "__main__":
    g = Generator()
    print(g.genGrid(1))