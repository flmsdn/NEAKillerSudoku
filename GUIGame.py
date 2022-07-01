from itertools import product
import tkinter as tk
import numpy as np
import tkinter.filedialog as fd
import tkinter.simpledialog as sd
import re
import sys

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
        self.__gameComplete = False
    
    # operations on colours
    #https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
    def __rgbToHex(self,rgb):
        return '#%02x%02x%02x' % rgb
    
    def __clamp(self,val):
        return sorted([0,val,255])[1]

    def __mulC(self,a,b):
        return tuple([ self.__clamp(round(a[x]*b[x])) for x in range(len(a))])
    
    def __addC(self,a,b):
        return tuple([self.__clamp(a[x]+b[x]) for x in range(len(a))])
    
    def __subC(self,a,b):
        return tuple([self.__clamp(a[x]-b[x]) for x in range(len(a))])

    def gameComplete(self):
        return self.__gameComplete
    
    def endGame(self):
        self.__gameComplete = True
    
    def resetGame(self):
        self.__selectedCell = None
        self.__gameComplete = False

    #open a new game in its own window
    def openWindow(self,saveFunction,loadFunction,quitFunction,undoFunction,redoFunction,solveFunction):
        self.gameWindow = tk.Toplevel()
        self.gameWindow.configure(bg=self.__rgbToHex(self.__colours["background"]))
        self.gameWindow.title("Game")
        self.gameWindow.state("zoomed")
        self.__dim = [self.gameWindow.winfo_screenwidth(),self.gameWindow.winfo_screenheight()]
        self.__selectedCell = None
        self.__gameComplete = False
        #sudoku grid
        self.__width = round(self.__dim[1]*0.7)
        self.gameGrid = tk.Canvas(self.gameWindow,width=self.__width,height=self.__width,highlightthickness=0)
        self.gameGrid.place(x=self.__dim[0]/2-self.__width/2,y=round(self.__dim[1]*0.45)-self.__width/2)
        #undo and redo images
        imgPath = sys.path[0]+r"\Resources"
        self.__undoImg = tk.PhotoImage(master=self.gameWindow,file=imgPath+r"\Undo.png",width=100,height=100)
        self.__redoImg = tk.PhotoImage(master=self.gameWindow,file=imgPath+r"\Redo.png",width=100,height=100)
        #undoLabel = tk.Label(image=self.__undoImg)
        redoLabel = tk.Label(image=self.__redoImg)
        #buttons
        buttonWidthReg = round(self.__dim[1]*0.25)
        buttonWidthSmall = round(self.__dim[1]*0.12)
        buttonHeight = round(self.__dim[1]*0.04)
        offsetHoriz = round(self.__dim[1]*0.025)
        offsetVert = round(self.__dim[1]*0.015)
        #button frames
        saveButtonFrame = tk.Frame(self.gameWindow)
        saveButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg-offsetHoriz,y=self.__dim[1]/2+self.__width/2-3*offsetVert,width=buttonWidthReg,height=buttonHeight)
        loadButtonFrame = tk.Frame(self.gameWindow)
        loadButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg-offsetHoriz,y=self.__dim[1]/2+self.__width/2,width=buttonWidthReg,height=buttonHeight)
        solveButtonFrame = tk.Frame(self.gameWindow)
        solveButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg-offsetHoriz,y=self.__dim[1]/2+self.__width/2+3*offsetVert,width=buttonWidthSmall,height=buttonHeight)
        quitButtonFrame = tk.Frame(self.gameWindow)
        quitButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthSmall-offsetHoriz,y=self.__dim[1]/2+self.__width/2+3*offsetVert,width=buttonWidthSmall,height=buttonHeight)
        undoButtonFrame = tk.Frame(self.gameWindow)
        undoButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthSmall,y=self.__dim[1]*0.45-self.__width/2-3*buttonHeight//2,width=100,height=100)
        redoButtonFrame = tk.Frame(self.gameWindow)
        redoButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg,y=self.__dim[1]*0.45-self.__width/2-3*buttonHeight//2,width=buttonWidthSmall,height=buttonHeight)
        #buttons
        self.saveButton = tk.Button(saveButtonFrame,text="Save",command=saveFunction)
        self.loadButton = tk.Button(loadButtonFrame,text="Load",command=loadFunction)
        self.solveButton = tk.Button(solveButtonFrame,text="Solve",command=solveFunction)
        self.quitButton = tk.Button(quitButtonFrame,text="Quit", command=quitFunction)
        self.undoButton = tk.Button(undoButtonFrame,text="Undo",image=self.__undoImg, command=undoFunction)
        self.redoButton = tk.Button(redoButtonFrame,text="Redo", command=redoFunction)
        self.saveButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.loadButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.solveButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.quitButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.undoButton.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        self.redoButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)

    #start the game window playing
    def startGame(self):
        self.gameWindow.mainloop()
    
    def closeGame(self):
        self.gameWindow.destroy()
    
    #return the selected cell
    def getSelected(self):
        return self.__selectedCell

    #calculate which cell has been clicked on in the canvas
    def cellClick(self,event):
        x,y = event.x, event.y
        cellWidth = self.__width/9
        gridCell = [int(x//cellWidth),int(y//cellWidth)]
        if gridCell[0]>8:
            gridCell[0]=8
        if gridCell[1]>8:
            gridCell[1]=8
        self.__selectedCell = gridCell

    def savePrompt(self):
        st = sd.askstring("Prompt","Enter a name to save as: ")
        return st
    
    def loadPrompt(self):
        st = fd.askopenfilename()
        matchObj = (re.match(r".*\/(.*\.json)$",st))
        return matchObj.groups()[0]

    #draws the current grid onto the canvas
    def updateGrid(self, grid, fixedCells):
        fontNormal = ('Helvetica','20')
        fontFixed = ('Helvetica','20','bold')
        npGrid = np.array(grid)
        #get line colours
        colDiff = self.__subC(self.__colours["line"],(128,128,128))
        colMul = self.__mulC(colDiff,(0.2,0.2,0.2))
        if self.__gameComplete:
            fade = (130,130,130)
            lineCol = self.__rgbToHex(self.__addC(self.__colours["line"],fade))
            inlineCol = self.__rgbToHex(self.__addC(self.__addC( (128,128,128), colMul),fade))
        else:
            lineCol = self.__rgbToHex(self.__colours["line"])
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
                self.gameGrid.create_text(centreOffset+c*cellWidth,centreOffset+r*cellWidth,text=str(npGrid[r,c]),font=(fontFixed if [c,r] in fixedCells else fontNormal),fill=lineCol)
        if self.__gameComplete:
            self.gameGrid.create_text(centreOffset+4*cellWidth,centreOffset+4*cellWidth,text="Well done! Game Complete",font=fontFixed)