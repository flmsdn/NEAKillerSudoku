import os, sys
import tkinter as tk
from Game import Game
from Colours import Colour
from GUIGame import GUIGame
import winsound

#Events are going to be used with Exception Handling
class GameFinish(Exception):
    pass

class Undo(Exception):
    pass

class Redo(Exception):
    pass

class Save(Exception):
    pass

class Load(Exception):
    pass

class Solve(Exception):
    pass

# Action class to contain actions for the undo and redo stacks
class Action():
    def __init__(self,x,y,before,after):
        self.x,self.y,self.before,self.after=x,y,before,after

# User Interface class that the Terminal and GUI will inherit from
class UI():
    def __init__(self,loadOption=0):
        self._gameOver = False
        self._actionStack = []
        self._redoStack = []
        self.Game = Game()

    #loop the game playing
    def run(self):
        while not self._gameOver:
            self.play()
    
    #control a move being played
    def playMove(self,x,y,val):
        action = Action(x,y,self.Game.getCell(x-1,y-1),val)
        self.Game.updateCell(x-1,y-1,val)
        self._actionStack.append(action)
        self._redoStack = []

    #undo move
    def undo(self):
        if not self._actionStack: return False
        action = self._actionStack.pop()
        self._redoStack.append(action)
        self.Game.updateCell(action.x-1,action.y-1,action.before)
        return True

    #redo move
    def redo(self):
        if not self._redoStack: return False
        action = self._redoStack.pop()
        self._actionStack.append(action)
        self.Game.updateCell(action.x-1,action.y-1,action.after)
        return True
    
    #save the current game to a game file
    def save(self,fileName,errors=0):
        if not fileName: return
        if len(fileName)>4 and fileName[-5:]!=".json":
            fileName+=".json"
        elif len(fileName)<5:
            fileName+=".json"
        self.Game.saveGame(fileName,errors)

    #load a game from a game file
    def load(self, fileName):
        if len(fileName)>4 and fileName[-5:]!=".json":
            fileName+=".json"
        elif len(fileName)<5:
            fileName+=".json"
        self.Game.loadGame(fileName)

    #play the game - the main game loop
    def play(self):
        raise NotImplementedError
    
    #display the current interface
    def display(self):
        raise NotImplementedError

    #end the program
    def gameOver(self):
        return self._gameOver

# Terminal UI
class Terminal(UI):
    def __init__(self, file=None):
        super().__init__(file)

    def run(self):
        print(Colour.BLUE+Colour.BOLD+"Sudoku"+Colour.ENDC+"\n")
        print(open("Instructions.txt").read(),"\n\nPress Enter to Play")
        input()
        super().run()

    def save(self, fileName=None):
        if fileName is None:
            fileName = input("Enter a name to save the file as (leave blank to not save):")
        super().save(fileName)
        print("Saved\n")

    def load(self,fileName=None):
        if fileName is None:
            games = os.listdir(sys.path[0]+"\\LocalGames")
            print("   ".join(games))
            fileName = input("Choose a file to load: ")
        super().load(fileName)

    def gridComplete(self):
        if self.Game.checkComplete():
            print("Well done! Game complete")
            if self.Game.getFile:
                prompt = input("Would you like to delete your game file? (y/n)")
                if prompt.lower() !=  "n":
                    self.Game.deleteGame()
        else:
            print("Incorrect")
        playAgain = input("\nPlay Again? (y/n): ").lower()
        if playAgain=="n":
            self._gameOver = True

    def play(self):
        i = input("Would you like to load a game or play a new game? (1/2)")
        if i=="1":
            #load game
            self.load()
        elif i=="2":
            #generate new game
            try:
                diff = int(input("Input a difficulty 1-7 (2 is default): "))
                if not 0<diff<8: raise ValueError
            except:
                diff = 2
            self.Game.newGame(diff)

        def validInp(text, val):
            value = input(text)
            gameEvents = {"t": GameFinish, "u": Undo, "r": Redo, "s": Save, "f": Solve } #use a dictionary to avoid long if statements
            if value.lower() in gameEvents:
                raise gameEvents[value.lower()]
            minValue = -1 if val else 0
            if not minValue<int(value)<10:
                raise ValueError
            else:
                return int(value)
        
        while True:
            self.display()
            if self.Game.checkFull():
                self.gridComplete()
                break
            while True:
                try:
                    x,y,val = validInp("Col to input (x coordinate): ",False), validInp("Row to input (y coordinate): ",False), validInp("Value: ",True)
                    if self.Game.checkCell(x-1,y-1):
                        break
                    else:
                        raise ValueError
                except GameFinish:
                    prompt = input("Do you want to save your game first? (y/n)")
                    if prompt.lower()=="y":
                        self.save()
                    self._gameOver = True
                    print("Game Terminated")
                    return
                except Undo:
                    if self.undo():
                        print("Action Undone")
                        self.display()
                    else:
                        print("There were no moves to Undo")
                except Redo:
                    if self.redo():
                        print("Action Redone")
                        self.display()
                    else:
                        print("There were no moves to Redo")
                except Save:
                    self.save()
                except Load:
                    prompt = input("Do you want to save your game first? (y/n)")
                    if prompt.lower()=="y":
                        self.save()
                    self.load()
                except Solve:
                    prompt = input("Are you sure you want to solve the grid? (y/n)")
                    if prompt.lower()=="y":
                        self.Game.solve()
                        self.display()
                        self.gridComplete()
                        return
                except:
                    print("Please input a valid number (between 1 and 9 inclusive)\n")
            print("\n")
            self.playMove(x,y,val)

    def display(self):
        if self.Game.getType() == 0:
            grid = self.Game.getGrid()
            printedGrid="  123 456 789\n"
            for row in range(9):
                printedGrid+=str(row+1)+" "
                for col in range(9):
                    if grid[row][col]!=0:
                        if self.Game.checkCell(col,row):
                            printedGrid+=str(grid[row][col])
                        else:
                            printedGrid+=Colour.BOLD+str(grid[row][col])+Colour.ENDC
                    else:
                        printedGrid+=" "
                    if col in (2,5): printedGrid+=Colour.BOLD+"|"+Colour.ENDC
                if row in (2,5): printedGrid+="\n  "+Colour.BOLD+"-"*11+Colour.ENDC
                printedGrid+="\n"
            print(printedGrid)
        else:
            pass

# Graphical User Interface
class GUI(UI):
    def __init__(self, file=None):
        super().__init__(file)
        self.__root = None
        self.__GUIGame = GUIGame()
        self.__errorCells = set()
        self.__errors = 0
        self.__audioPath = sys.path[0]+"\\Resources\\Sounds\\"
        self.__audioPreset = "retro"
        self.__soundsDict = {0:"Write.wav",1: "Win.wav",2: "Gameover.wav"}

    def playSound(self,id):
        winsound.PlaySound(self.__audioPath+self.__audioPreset+self.__soundsDict[id], winsound.SND_ASYNC | winsound.SND_ALIAS)

    def __startMenu(self):
        self.__root = tk.Tk()
        self.__root.title("Main Menu")
        self.__root.state("zoomed")
        self.__dim = [self.__root.winfo_screenwidth(),self.__root.winfo_screenheight()]
        buttonWidth = round(self.__dim[0]*0.1)
        buttonHeight = round(self.__dim[0]*0.02)
        offsetHoriz = round(self.__dim[0]*0.01)
        offsetVert = round(self.__dim[0]*0.2)
        #play
        playFrame = tk.Frame(self.__root)
        playFrame.place(x=self.__dim[0]//2-buttonWidth-offsetHoriz,y=offsetVert,width=buttonWidth,height=buttonHeight)
        playButton = tk.Button(playFrame,text="Play", command=self.playRandom)
        playButton.pack(expand=True,fill=tk.BOTH)
        #load
        loadFrame = tk.Frame(self.__root)
        loadFrame.place(x=self.__dim[0]//2+offsetHoriz,y=offsetVert,width=buttonWidth,height=buttonHeight)
        loadButton = tk.Button(loadFrame,text="Load", command=self.playLoad)
        loadButton.pack(expand=True,fill=tk.BOTH)
        games = os.listdir(sys.path[0]+"\\LocalGames")
        self.__gameOption = tk.StringVar()
        self.__gameOption.set(games[0])
        optionDropDown = tk.OptionMenu(self.__root,self.__gameOption,*games)
        optionDropDown.place(x=self.__dim[0]//2+offsetHoriz,y=offsetVert+round(self.__dim[1]*0.05))
        #quit
        quitFrame = tk.Frame(self.__root)
        quitFrame.place(x=round(self.__dim[0]*0.95)-buttonWidth,y=round(self.__dim[1]*0.92)-buttonHeight,width=buttonWidth,height=buttonHeight)
        quitButton = tk.Button(quitFrame,text="Quit", command=self.gameOver)
        quitButton.pack(expand=True,fill=tk.BOTH)
        #difficulty slider
        sliderFrame = tk.Frame(self.__root)
        sliderFrame.place(x=self.__dim[0]//2-buttonWidth-offsetHoriz,y=round(self.__dim[1]*0.32)+buttonHeight,width=buttonWidth,height=buttonHeight*2)
        text = tk.Label(sliderFrame, text="Difficulty: ")
        text.pack()
        self.__difficultySlider = tk.Scale(sliderFrame, from_=1, to=7, orient=tk.HORIZONTAL)
        self.__difficultySlider.pack(expand=True,fill=tk.X)

    def playMove(self, x, y, val):
        super().playMove(x, y, val)
        self.__errorCells = self.Game.getErrorCells()

    def __gameScreen(self):
        self.__GUIGame.openWindow(self.saveButton,self.loadButton,self.closeGame,self.undoButton,self.redoButton,self.solveButton)
        self.eventSetup()
        self.display()
        self.__GUIGame.startGame()

    def closeMenu(self):
        pass

    def closeGame(self):
        #TODO add prompt for saving
        self.__GUIGame.closeGame()
    
    def undo(self,event):
        self.undoButton()

    def redo(self,event):
        self.redoButton()
    
    def solve(self,event):
        self.solveButton()

    def save(self, event):
        self.saveButton()
    
    def load(self,event):
        self.loadButton()
    
    def toggleWrite(self,event):
        self.Game.toggleWrite()

    def playRandom(self):
        self.Game.newGame(self.__difficultySlider.get())
        self.__errorCells = self.Game.getErrorCells()
        self.__errors = 0
        self.__gameScreen()
    
    def playLoad(self):
        self.loadButton(play=True)
        self.__gameScreen()

    def undoButton(self):
        if self.__GUIGame.gameComplete(): return
        if super().undo():
            self.__errorCells = self.Game.getErrorCells()
            self.display()

    def redoButton(self):
        if super().redo():
            self.display()

    def solveButton(self):
        self.Game.solve()
        self.__GUIGame.endGame()
        self.display()
        
    def loadButton(self, play=False):
        if play:
            value=self.__gameOption.get()
            super().load(value)
            self.__errorCells = self.Game.getErrorCells()
            self.__errors = self.Game.getErrors()
            return
        fileName = self.__GUIGame.loadPrompt()
        if fileName:
            super().load(fileName)
            self.__GUIGame.resetGame()
            self.__errorCells = self.Game.getErrorCells()
            self.__errors = self.Game.getErrors()
            self.display()

    def saveButton(self):
        fileName = self.__GUIGame.savePrompt()
        super().save(fileName,self.__errors)

    def clickCanvas(self,event):
        self.__GUIGame.cellClick(event)
        self.display()

    def eventSetup(self):
        self.__GUIGame.gameGrid.bind("<Button 1>",self.clickCanvas)
        for number in range(1,10):
            self.__GUIGame.gameWindow.bind(str(number),self.__numInput)
        self.__GUIGame.gameWindow.bind("<Key-BackSpace>",self.__numInput)
        gameEvents = {"t": self.closeGame, "u": self.undo, "r": self.redo, "s": self.save, "f": self.solve, "p": self.toggleWrite } #use a dictionary to avoid long if statements
        for x in gameEvents:
            self.__GUIGame.gameWindow.bind(x,gameEvents[x])
        self.__GUIGame.gameWindow.bind("<Configure>",self.resize)

    def resize(self,event):
        self.__GUIGame.resize(event)
        self.display()
        
    def __numInput(self,event):
        if self.__GUIGame.gameComplete(): return
        if event.keycode==8:
            cell = self.__GUIGame.getSelected()
            if self.Game.checkCell(cell[0],cell[1]):
                self.playMove(cell[0]+1,cell[1]+1,0)
                self.display()
        err = self.__errorCells
        if 48<event.keycode<58:
            value = event.keycode-48
            cell = self.__GUIGame.getSelected()
            if self.Game.checkCell(cell[0],cell[1]):
                self.playMove(cell[0]+1,cell[1]+1,value)
                #play sound
                self.playSound(0)
                if self.__errorCells!=err and self.__errorCells:
                    self.__errors+=1
                    if self.__errors>2:
                        self.__GUIGame.gameOver()
                        self.playSound(2)
                if self.Game.checkFull():
                    if self.Game.checkComplete():
                        self.__GUIGame.endGame()
                        self.playSound(1)
                self.display()


    def run(self):
        self.__startMenu()
        self.__root.mainloop()

    def display(self):
        self.__GUIGame.updateGrid(self.Game.getGrid(),self.Game.fixedCells(),self.__errorCells,self.__errors,self.Game.getPencilMarkings())
    
    def gameOver(self):
        self.gameOver = True
        self.__root.destroy()
        self.__root = None

if __name__ == "__main__":
    pass