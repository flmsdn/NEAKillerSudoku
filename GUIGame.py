from itertools import product
import tkinter as tk

class GUIGame():
    def __init__(self):
        self.__gameWindow = None
        self.__gameGrid = None
        self.__dim = [None,None]
        self.__width = 0
        self.__colours = {"line": (0,0,0), "background": (255,255,255), "canvas": (255,255,255)}
    
    def openWindow(self):
        self.__gameWindow = tk.Tk()
        self.__gameWindow.configure(bg=self.rgbToHex(self.__colours["background"]))
        self.__gameWindow.title("Game")
        self.__gameWindow.state("zoomed")
        self.__dim = [self.__gameWindow.winfo_screenwidth(),self.__gameWindow.winfo_screenheight()]
        self.__width = self.__dim[1]*0.7
        self.__gameGrid = tk.Canvas(self.__gameWindow,width=self.__width,height=self.__width,highlightthickness=0)
        self.__gameGrid.place(x=self.__dim[0]/2-self.__width/2,y=self.__dim[1]/2-self.__width/2)
        self.updateGrid()
        self.__gameGrid.mainloop()

    def rgbToHex(self,rgb):
        return '#%02x%02x%02x' % rgb
    
    def mulC(self,a,b):
        return tuple([ round(a[x]*b[x]) for x in range(len(a))])
    
    def addC(self,a,b):
        return tuple([a[x]+b[x] for x in range(len(a))])
    
    def subC(self,a,b):
        return tuple([a[x]-b[x] for x in range(len(a))])
    
    def updateGrid(self):
        outlineWidth = 6
        innerWidth = 2
        nonetWidth = 4
        lineCol = self.rgbToHex(self.__colours["line"])
        #get inner line colour
        colDiff = self.subC(self.__colours["line"],(128,128,128))
        colMul = self.mulC(colDiff,(0.2,0.2,0.2))
        inlineCol = self.rgbToHex(self.addC( (128,128,128), colMul))
        oS = outlineWidth//2
        mi, ms, ma, l = oS, self.__width, self.__width-oS, (self.__width-2*oS)/9
        self.__gameGrid.delete("all")
        #inner lines
        for r in [1,2,4,5,7,8]:
            self.__gameGrid.create_line(mi+r*l, 0, mi+r*l, ms, width=innerWidth,fill=inlineCol)
            self.__gameGrid.create_line(0, mi+r*l, ms, mi+r*l, width=innerWidth,fill=inlineCol)
        #outline
        self.__gameGrid.create_line(mi, 0, mi, ms, width=outlineWidth,fill=lineCol)
        self.__gameGrid.create_line(0, ma, ms, ma, width=outlineWidth,fill=lineCol)
        self.__gameGrid.create_line(ma, 0, ma, ms, width=outlineWidth,fill=lineCol)
        self.__gameGrid.create_line(0, mi, ms, mi, width=outlineWidth,fill=lineCol)
        #nonet outlines
        for r in [3,6]:
            self.__gameGrid.create_line(mi+r*l, 0, mi+r*l, ms, width=nonetWidth,fill=lineCol)
            self.__gameGrid.create_line(0, mi+r*l, ms, mi+r*l, width=nonetWidth,fill=lineCol)