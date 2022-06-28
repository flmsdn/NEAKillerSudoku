from itertools import product
import tkinter as tk
import numpy as np

# handles the Tkinter for the GUI
class GUIGame():
    # class constants
    GRID_OUTLINE = 6
    GRID_NONET = 4
    GRID_INNER = 2

    def __init__(self):
        self.gameWindow = None
        self.gameGrid = None
        self.__dim = [None,None]
        self.__width = 0
        #all colours are stored as RGB but must be converted to hexadecimal for Tkinter
        self.__colours = {"line": (0,0,0), "background": (255,255,255), "canvas": (255,255,255)}
        self.__selectedCell = None
    
    # operations on colours
    def __rgbToHex(self,rgb):
        return '#%02x%02x%02x' % rgb
    
    def __mulC(self,a,b):
        return tuple([ round(a[x]*b[x]) for x in range(len(a))])
    
    def __addC(self,a,b):
        return tuple([a[x]+b[x] for x in range(len(a))])
    
    def __subC(self,a,b):
        return tuple([a[x]-b[x] for x in range(len(a))])

    #open a new game in its own window
    def openWindow(self):
        self.gameWindow = tk.Tk()
        self.gameWindow.configure(bg=self.__rgbToHex(self.__colours["background"]))
        self.gameWindow.title("Game")
        self.gameWindow.state("zoomed")
        self.__dim = [self.gameWindow.winfo_screenwidth(),self.gameWindow.winfo_screenheight()]
        self.__width = self.__dim[1]*0.7
        self.gameGrid = tk.Canvas(self.gameWindow,width=self.__width,height=self.__width,highlightthickness=0)
        self.gameGrid.place(x=self.__dim[0]/2-self.__width/2,y=self.__dim[1]/2-self.__width/2)

    #start the game window playing
    def startGame(self):
        self.gameWindow.mainloop()
    
    #return the selected cell
    def getSelected(self):
        return self.__selectedCell

    #calculate which cell has been clicked on in the canvas
    def cellClick(self,event):
        x,y = event.x, event.y
        cellWidth = self.__width/9
        gridCell = [int(y//cellWidth),int(x//cellWidth)]
        if gridCell[0]>8:
            gridCell[0]=8
        if gridCell[1]>8:
            gridCell[1]=8
        self.__selectedCell = gridCell

    #draws the current grid onto the canvas
    def updateGrid(self, grid, fixedCells):
        fontNormal = ('Helvetica','20')
        fontFixed = ('Helvetica','20','bold')
        npGrid = np.array(grid)
        lineCol = self.__rgbToHex(self.__colours["line"])
        #get inner line colour
        colDiff = self.__subC(self.__colours["line"],(128,128,128))
        colMul = self.__mulC(colDiff,(0.2,0.2,0.2))
        inlineCol = self.__rgbToHex(self.__addC( (128,128,128), colMul))
        oS = self.GRID_OUTLINE//2
        mi, ms, ma, l = oS, self.__width, self.__width-oS, (self.__width-2*oS)/9
        self.gameGrid.delete("all")
        #inner lines
        for r in [1,2,4,5,7,8]:
            self.gameGrid.create_line(mi+r*l, 0, mi+r*l, ms, width=self.GRID_INNER,fill=inlineCol)
            self.gameGrid.create_line(0, mi+r*l, ms, mi+r*l, width=self.GRID_INNER,fill=inlineCol)
        #outline
        for n in (mi,ma):
            self.gameGrid.create_line(n, 0, n, ms, width=self.GRID_OUTLINE,fill=lineCol)
            self.gameGrid.create_line(0, n, ms, n, width=self.GRID_OUTLINE,fill=lineCol)
        #nonet outlines
        for r in [3,6]:
            self.gameGrid.create_line(mi+r*l, 0, mi+r*l, ms, width=self.GRID_NONET,fill=lineCol)
            self.gameGrid.create_line(0, mi+r*l, ms, mi+r*l, width=self.GRID_NONET,fill=lineCol)
        cellWidth, centreOffset = self.__width/9, self.__width/18
        for r,c in product(range(9),range(9)):
            if npGrid[r,c]:
                self.gameGrid.create_text(centreOffset+r*cellWidth,centreOffset+c*cellWidth,text=str(npGrid[r,c]),font=(fontFixed if [c,r] in fixedCells else fontNormal))