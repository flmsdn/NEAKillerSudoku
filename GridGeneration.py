import itertools
import random
import numpy as np
import sys
import json

# Generator class for making and solving Sudoku grids
class Generator():
    def __init__(self):
        self.__nums = list(range(1,10))
        self.__count = 0
        #use a config file for shapes - this allows us to change the values easily outside of the code and makes code easier to read
        shapeCfgFile = open(sys.path[0]+r"\Resources\config\shapes.json","r")
        self.__shapeConfig = json.load(shapeCfgFile)
    
    def check(self,test,array): #https://codereview.stackexchange.com/questions/193835/checking-a-one-dimensional-numpy-array-in-a-multidimensional-array-without-a-loo
        return any(np.array_equal(x, test) for x in array)

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
                return gridTrial.tolist()
    
    def genGrid(self, difficulty):
        grid = np.array([[0]*9]*9,ndmin=2) #empty grid
        self.fillGrid(grid) #fill grid in with random values
        #limit difficulty
        if difficulty>7: difficulty=7
        elif difficulty<1: difficulty=1
        while difficulty:
            #optimised randomly getting a cell
            cells = list(zip(*np.where(grid>0)))
            r,c = random.choice(cells)
            oldVal = grid[r,c]
            grid[r,c]=0
            #copy grid so no permanent change are made
            gridCopy = np.copy(grid)
            self.__count=0
            self.iterateGrid(gridCopy,False)
            if self.__count!=1:
                grid[r,c]=oldVal
                difficulty-=1
        return grid.tolist()
    
    def findShape(self,grid,shape):
        usedCoords = []
        #shape coordinates are in the form [y,x]
        #extract all numbers in the shape and the shape coordinates
        nums = shape[0]
        shapeCoords = shape[1]
        #get all coordinates of each number in the shape in a new array
        numCoords = [(np.argwhere(grid == n)) for n in nums]
        #now loop through each number
        shapes = [] #this will contain all of the shapes that match the given criteria
        for e,coords in enumerate(numCoords):
            for coord in coords:
                if list(coord) in usedCoords: break
                unusedInd = [i for i in range(len(nums)) if i!=e] #we store the indices of used numbers in the shape so far
                unusedCoords = shapeCoords[1:]
                foundShape = True
                curShape = [list(coord)]
                while len(unusedCoords):
                    foundCoord = False
                    checkCoord = [coord[0]+unusedCoords[-1][0],coord[1]+unusedCoords[-1][1]]
                    for i in unusedInd:
                        if self.check(np.array(checkCoord), numCoords[i]) and not (checkCoord in usedCoords):
                            foundCoord=True
                            curShape.append(checkCoord)
                            unusedInd.remove(i)
                            unusedCoords.pop()
                            break
                    if not foundCoord:
                        foundShape = False
                        break
                if foundShape:
                    shapes.append(curShape) #add the shape coordinates to the found shapes
                    usedCoords = usedCoords + curShape
        return shapes
    
    def checkForDefiniteCages(self,grid):
        #copy the filled grid
        tempG = np.copy(grid)
        #check for definite 5 cages all the way down to 2
        #after a cage is found we have a copy of the grid which removes the cage cells (to stop overlaps)
        #for each of the sizes (5 to 2) we need a set of shapes and sums
        shapes = self.__shapeConfig["shapes"] #ind 0 is size 2, 1 is size 3... 3 is size 5
        numbers = self.__shapeConfig["numbers"]
        cages = []
        for i in range(4):
            #i 0 is 5, i 3 is 2
            indShapes = shapes[3-i]
            indNumbers = numbers[3-i]
            for s in indShapes:
                for ns in indNumbers:
                    coordinates = self.findShape(tempG, [ns,s] )
                    if len(coordinates):
                        for cage in coordinates: #remove each found cage
                            #cages are stored with x,y coordinates but here it is easier to find y,x so we have to reverse them
                            cReverse = []
                            for point in cage:
                                tempG[ point[0],point[1] ] = 0
                                cReverse.append([point[1],point[0]])
                            cages.append( [sum(ns)] + cReverse )
        return tempG, cages #return the grid with uncaged cells and the cages

    def fillInFinalCages(self,tempGrid):
        shapes = self.__shapeConfig["reducedShapes"] #ind 0 is size 2, 1 is size 3... 3 is size 5
        cages = []
        for i in range(4):
            #i 0 is 4, i 3 is 1
            indShapes = shapes[3-i]
            for s in indShapes:
                coordinates = self.findShape(tempGrid, [range(1,10),s])
                if len(coordinates):
                    for cage in coordinates:
                        cReverse = []
                        cSum = 0
                        for point in cage:
                            cSum += tempGrid[point[0],point[1]]
                            tempGrid[point[0],point[1]] = 0
                            cReverse.append([point[1],point[0]])
                        cages.append( [cSum] + cReverse )
        return tempGrid, cages
    
    def iterateKillerGrid(self,grid,saveState,cageDict,cages):
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

    def genKillerGrid(self,difficulty):
        grid = np.array([[0]*9]*9,ndmin=2) #empty grid
        self.fillGrid(grid) #fill grid in with random values
        #limit difficulty
        if difficulty>7: difficulty=7
        elif difficulty<1: difficulty=1
        emptiedGrid, cages = self.checkForDefiniteCages(grid) #we get the definite cages, leaving cells that cannot fit in these
        #now we need to find a way to create cages around remaining cells
        #we create cages around remaining cells, avoiding certain shapes to make the puzzle more varied
        emptiedGrid,newCages = self.fillInFinalCages(emptiedGrid)
        '''
        while difficulty:
            #optimised randomly getting a cell
            cells = list(zip(*np.where(grid>0)))
            r,c = random.choice(cells)
            oldVal = grid[r,c]
            grid[r,c]=0
            #copy grid so no permanent change are made
            gridCopy = np.copy(grid)
            self.__count=0
            self.iterateKillerGrid(gridCopy,False)
            if self.__count!=1:
                grid[r,c]=oldVal
                difficulty-=1'''
        grid = np.array([[0]*9]*9,ndmin=2) #empty grid
        return grid.tolist(), (cages+newCages)

if __name__ == "__main__":
    pass