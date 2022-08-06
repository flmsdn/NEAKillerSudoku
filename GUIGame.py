from distutils.log import error
from itertools import product
import tkinter as tk
import numpy as np
import tkinter.filedialog as fd
import tkinter.simpledialog as sd
import re, sys
from PIL import Image, ImageTk
import playsound as ps

# handles the Tkinter for the GUI
class GUIGame():
    # class constants
    GRID_OUTLINE = 6
    GRID_NONET = 4
    GRID_INNER = 2

    def __init__(self):
        self.__errorChecking = True
        self.gameWindow = None
        self.gameGrid = None
        self.__dim = [None,None]
        self.__width = 0
        #all colours are stored as RGB but must be converted to hexadecimal for Tkinter
        self.__colours = {"line": (0,0,0), "background": (255,255,255), "canvas": (255,255,255), "selected": (180,180,180), "selectedRC": (220,220,220),"errorCell": (255,180,180),"error": (255,0,0)}
        self.__selectedCell = None
        self.__gameComplete = False
        self.__gameOver = False
        self.__writeMode = "Pencil"
    
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
        return self.__gameComplete or self.__gameOver
    
    def gameOver(self):
        self.__gameOver = True
    
    def endGame(self):
        self.__gameComplete = True
    
    def resetGame(self):
        self.__selectedCell = None
        self.__gameComplete = False

    def updateWriteMode(self):
        self.__writeMode = "Pen" if self.__writeMode ==  "Pencil" else "Pencil"
        self.writeModeButton.config(text=self.__writeMode)
    
    #open a new game in its own window
    def openWindow(self,saveFunction,loadFunction,quitFunction,undoFunction,redoFunction,solveFunction,toggleWriteMode):
        self.gameWindow = tk.Toplevel()
        self.gameWindow.configure(bg=self.__rgbToHex(self.__colours["background"]))
        self.gameWindow.title("Game")
        self.gameWindow.state("zoomed")
        self.gameWindow.resizable(True,True)
        self.__dim = [self.gameWindow.winfo_screenwidth(),self.gameWindow.winfo_screenheight()]
        self.__selectedCell = None
        self.__gameComplete = False
        self.__gameOver = False
        self.__functions = [saveFunction,loadFunction,quitFunction,undoFunction,redoFunction,solveFunction,toggleWriteMode]
        #sudoku grid
        self.__width = round(self.__dim[1]*0.7)
        self.gameGrid = tk.Canvas(self.gameWindow,width=self.__width,height=self.__width,highlightthickness=0)
        self.gameGrid.place(x=self.__dim[0]/2-self.__width/2,y=round(self.__dim[1]*0.45)-self.__width/2)
        self.loadSizedWindow()
    
    def loadSizedWindow(self):
        for widget in self.gameWindow.winfo_children():
            if type(widget)!=tk.Canvas:
                widget.destroy()
        #undo and redo images
        self.__width = round(self.__dim[1]*0.7)
        scale = self.__width/self.gameGrid.winfo_width()
        self.gameGrid.config(width = self.__width,height=self.__width)
        self.gameGrid.place(x=self.__dim[0]/2-self.__width/2,y=round(self.__dim[1]*0.45)-self.__width/2)
        #self.gameGrid.scale("all",0,0,scale,scale)
        imLen = round(self.__dim[1]*0.05)
        crossLen = round(self.__dim[1]*0.1)
        imOffset = round(self.__dim[1]*0.12)
        imgPath = sys.path[0]+r"\Resources"
        undoI = Image.open(imgPath+r"\Undo.png").resize((imLen,imLen))
        redoI = Image.open(imgPath+r"\Redo.png").resize((imLen,imLen))
        emptyI = Image.open(imgPath+r"\EmptyCross.png").resize((crossLen*2,crossLen*2))
        errorI = Image.open(imgPath+r"\ErrorCross.png").resize((crossLen*2,crossLen*2))
        self.__undoImg = ImageTk.PhotoImage(undoI)
        self.__redoImg = ImageTk.PhotoImage(redoI)
        self.__emptyCross = ImageTk.PhotoImage(emptyI)
        self.__errorCross = ImageTk.PhotoImage(errorI)
        #buttons
        buttonWidthReg = round(self.__dim[1]*0.25)
        buttonWidthSmall = round(self.__dim[1]*0.12)
        buttonHeight = round(self.__dim[1]*0.04)
        offsetHoriz = round(self.__dim[1]*0.025)
        offsetVert = round(self.__dim[1]*0.015)
        #button frames
        saveButtonFrame = tk.Frame(self.gameWindow)
        saveButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg-offsetHoriz,y=self.__dim[1]/2+self.__width/2,width=buttonWidthReg,height=buttonHeight)
        loadButtonFrame = tk.Frame(self.gameWindow)
        loadButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg-offsetHoriz,y=self.__dim[1]/2+self.__width/2+3*offsetVert,width=buttonWidthReg,height=buttonHeight)
        solveButtonFrame = tk.Frame(self.gameWindow)
        solveButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthReg-offsetHoriz,y=self.__dim[1]/2+self.__width/2+6*offsetVert,width=buttonWidthSmall,height=buttonHeight)
        quitButtonFrame = tk.Frame(self.gameWindow)
        quitButtonFrame.place(x=self.__dim[0]/2+self.__width/2-buttonWidthSmall-offsetHoriz,y=self.__dim[1]/2+self.__width/2+6*offsetVert,width=buttonWidthSmall,height=buttonHeight)
        undoButtonFrame = tk.Frame(self.gameWindow)
        undoButtonFrame.place(x=self.__dim[0]/2+self.__width/2-imOffset,y=self.__dim[1]*0.45-self.__width/2-3*buttonHeight//2) #width and height
        redoButtonFrame = tk.Frame(self.gameWindow)
        redoButtonFrame.place(x=self.__dim[0]/2+self.__width/2-imLen,y=self.__dim[1]*0.45-self.__width/2-3*buttonHeight//2)
        writeModeFrame = tk.Frame(self.gameWindow)
        writeModeFrame.place(x=self.__dim[0]/2+self.__width/2-imLen-imOffset,y=self.__dim[1]*0.45-self.__width/2-3*buttonHeight//2)
        #buttons
        self.saveButton = tk.Button(saveButtonFrame,text="Save",command=self.__functions[0])
        self.loadButton = tk.Button(loadButtonFrame,text="Load",command=self.__functions[1])
        self.solveButton = tk.Button(solveButtonFrame,text="Solve",command=self.__functions[5])
        self.quitButton = tk.Button(quitButtonFrame,text="Quit", command=self.__functions[2])
        self.undoButton = tk.Button(undoButtonFrame,image=self.__undoImg, command=self.__functions[3])
        self.undoButton.image = self.__undoImg
        self.redoButton = tk.Button(redoButtonFrame,image=self.__redoImg, command=self.__functions[4])
        self.redoButton.image = self.__redoImg
        self.writeModeButton = tk.Button(writeModeFrame,text=self.__writeMode, command=self.__functions[6])
        self.saveButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.loadButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.solveButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.quitButton.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.undoButton.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        self.redoButton.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        self.writeModeButton.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        self.errorCrosses = [None]*3
        for cross in range(3):
            errorFrame = tk.Frame(self.gameWindow)
            errorFrame.place(x=self.__dim[0]/2-self.__width/2 + cross*crossLen,y=self.__dim[1]/2+self.__width/2,width=crossLen,height=crossLen)
            self.errorCrosses[cross] = tk.Label(errorFrame, image = self.__emptyCross, background=self.__rgbToHex(self.__colours["background"]))
            self.errorCrosses[cross].image = self.__emptyCross
            self.errorCrosses[cross].pack(side=tk.LEFT,expand=True,fill=tk.BOTH)

    def resize(self,event):
        if [event.width,event.height]!=self.__dim:
            if type(event.widget)==tk.Toplevel:
                #the window has been resized
                self.__dim = [event.width,event.height]
                self.loadSizedWindow()

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
        if not self.__selectedCell == gridCell:
            self.__selectedCell = gridCell

    def savePrompt(self):
        st = sd.askstring("Prompt","Enter a name to save as: ")
        return st
    
    def loadPrompt(self):
        st = fd.askopenfilename()
        matchObj = (re.match(r".*\/(.*\.json)$",st))
        if matchObj is None: return ""
        return matchObj.groups()[0]

    def traverseCage(self,cageCells,offset):
        points = []
        x,y = cageCells[0]
        dir=1
        translations = [[0,-1],[1,0],[0,1],[-1,0]]
        cornerPoints = [[-offset,offset],[-offset,-offset],[offset,-offset],[offset,offset]]
        if len(cageCells)==1:
            return [[x+a[0],y+a[1]] for a in cornerPoints]
        done=False
        while not done:
            #check directions, starting counterclockwise 90 degrees
            for direction in [(dir-1+x)%4 for x in range(4)]:
                #check this direction
                nCell = [x+translations[direction][0],y+translations[direction][1]]
                if nCell in cageCells:
                    dCount = (direction-dir+2)%4
                    if dCount == 0: dCount=4
                    for p in [cornerPoints[(dir+a)%4] for a in range(dCount)]:
                        nPoint = [x+p[0],y+p[1]]
                        points.append(nPoint)
                        if len(points)>1:
                            if nPoint == points[0]:
                                done = True
                                break
                    x,y = nCell
                    dir = direction
                    break
        return points

    #draws the current grid onto the canvas
    def updateGrid(self, grid, fixedCells, errorCells=None,errorCount=0,pencilMarkings=None,cages=None,cageDict=None):
        if errorCount>0:
            for err in range(len(self.errorCrosses)):
                if err<errorCount:
                    self.errorCrosses[err].configure(image = self.__errorCross)
                    self.errorCrosses[err].image = self.__errorCross
        fontNormal = ('Helvetica','20')
        fontFixed = ('Helvetica','20','bold')
        fontPencil = ('Helvetica','9')
        if cages:
            fontSum = ("Helvetica",'8')
        npGrid = np.array(grid)
        #get line colours
        colDiff = self.__subC(self.__colours["line"],(128,128,128))
        colMul = self.__mulC(colDiff,(0.2,0.2,0.2))
        if self.__gameComplete or self.__gameOver:
            fade = (130,130,130)
            lineCol = self.__rgbToHex(self.__addC(self.__colours["line"],fade))
            inlineCol = self.__rgbToHex(self.__addC(self.__addC( (128,128,128), colMul),fade))
        else:
            lineCol = self.__rgbToHex(self.__colours["line"])
            inlineCol = self.__rgbToHex(self.__addC( (128,128,128), colMul))
        oS = self.GRID_OUTLINE//2
        mi, ms, ma, l = oS, self.__width, self.__width-oS, (self.__width-2*oS)/9
        self.gameGrid.delete("all")
        cellWidth, centreOffset = (self.__width)/9, self.__width/18
        #highlighting selected cell
        if not self.__selectedCell is None:
            nx, ny = self.__selectedCell[0]//3-1, self.__selectedCell[1]//3-1
            #highlighting row and column
            self.gameGrid.create_rectangle(0,mi+l*self.__selectedCell[1],ms,mi+l*(self.__selectedCell[1]+1),fill=self.__rgbToHex(self.__colours["selectedRC"]),outline="")
            self.gameGrid.create_rectangle(mi+l*self.__selectedCell[0],0,mi+l*(self.__selectedCell[0]+1),ms,fill=self.__rgbToHex(self.__colours["selectedRC"]),outline="")
            self.gameGrid.create_rectangle(mi+l*self.__selectedCell[0],mi+l*self.__selectedCell[1],mi+l*(self.__selectedCell[0]+1),mi+l*(self.__selectedCell[1]+1),fill=self.__rgbToHex(self.__colours["selected"]),outline="")
        for r,c in product(range(9),range(9)):
            if npGrid[r,c]:
                if self.__errorChecking and (c,r) in errorCells:
                    self.gameGrid.create_rectangle(mi+l*c,mi+l*r,mi+l*(c+1),mi+l*(r+1),fill=self.__rgbToHex(self.__colours["errorCell"]),outline="")
                    self.gameGrid.create_text(centreOffset+c*cellWidth,centreOffset+r*cellWidth,text=str(npGrid[r,c]),font=(fontFixed if [c,r] in fixedCells else fontNormal),fill=self.__rgbToHex(self.__colours["error"]))
                else:
                    if not self.__selectedCell is None:
                        if npGrid[r,c]==npGrid[self.__selectedCell[1],self.__selectedCell[0]] and [c,r]!=self.__selectedCell:
                            self.gameGrid.create_rectangle(mi+l*c,mi+l*r,mi+l*(c+1),mi+l*(r+1),fill=self.__rgbToHex(self.__colours["selectedRC"]),outline="")
                    self.gameGrid.create_text(centreOffset+c*cellWidth,centreOffset+r*cellWidth,text=str(npGrid[r,c]),font=(fontFixed if [c,r] in fixedCells else fontNormal),fill=lineCol)
            elif type(pencilMarkings)==list:
                if pencilMarkings[r][c] != None and pencilMarkings[r][c] != []:
                    for pencilMark in pencilMarkings[r][c]:
                        xOffset = (pencilMark-1)%3+1
                        yOffset = (pencilMark-1)//3+1
                        self.gameGrid.create_text(xOffset*centreOffset//2+c*cellWidth,yOffset*centreOffset//2+r*cellWidth,text=str(pencilMark),font=fontPencil,fill=lineCol)
        if cages:
            sideOffset = 3/8
            for c in cages:
                val = c.sum
                x,y = c.cells[0]
                self.gameGrid.create_text(mi+centreOffset//4+x*l,mi+centreOffset//4+y*l,text=str(val),font=fontSum,fill=lineCol)
                points = self.traverseCage(c.cells,sideOffset)
                #generate cage lines
                self.gameGrid.create_polygon(*[mi+x*l+centreOffset for xs in points for x in xs],fill="",dash=(3,1,1,1),outline=inlineCol)
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
        if self.__gameComplete:
            self.gameGrid.create_text(centreOffset+4*cellWidth,centreOffset+4*cellWidth,text="Well done! Game Complete",font=fontFixed)
        elif self.__gameOver:
            self.gameGrid.create_text(centreOffset+4*cellWidth,centreOffset+4*cellWidth,text="Game Over",font=fontFixed)