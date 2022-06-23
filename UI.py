import os, sys
from Game import Game
from Colours import Colour

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

class Action():
    def __init__(self,x,y,before,after):
        self.x,self.y,self.before,self.after=x,y,before,after

class UI():
    def __init__(self,loadOption=0):
        self._gameOver = False
        self._actionStack = []
        self._redoStack = []
        self.Game = Game()

    def run(self):
        while not self._gameOver:
            self.play()
    
    def playMove(self,x,y,val):
        action = Action(x,y,self.Game.getCell(x-1,y-1),val)
        self.Game.updateCell(x-1,y-1,val)
        self._actionStack.append(action)
        self._redoStack = []

    def undo(self):
        if not self._actionStack: return False
        action = self._actionStack.pop()
        self._redoStack.append(action)
        print(action.x-1,action.y-1,action.before,action.after)
        self.Game.updateCell(action.x-1,action.y-1,action.before)
        return True
    
    def redo(self):
        if not self._redoStack: return False
        action = self._redoStack.pop()
        self._actionStack.append(action)
        self.Game.updateCell(action.x-1,action.y-1,action.after)
        return True
    
    def save(self):
        fileName = input("Enter a name to save the file as (leave blank to not save):")
        if not fileName: return
        if len(fileName)>4 and fileName[-5:]!=".json":
            fileName+=".json"
        self.Game.saveGame(fileName)
        print("Saved\n")

    def load(self):
        games = os.listdir(sys.path[0]+"\\LocalGames")
        print("   ".join(games))
        fileName = input("Choose a file to load: ")
        if len(fileName)>4 and fileName[-5:]!=".json":
            fileName+=".json"
        self.Game.loadGame(fileName)

    def play(self):
        raise NotImplementedError
    
    def display(self):
        raise NotImplementedError

    def gameOver(self):
        return self._gameOver

class Terminal(UI):
    def __init__(self, file=None):
        super().__init__(file)

    def run(self):
        print(Colour.BLUE+Colour.BOLD+"Sudoku"+Colour.ENDC+"\n")
        print(open("Instructions.txt").read(),"\n\nPress Enter to Play")
        input()
        super().run()

    def play(self):
        i = input("Would you like to load a game or play a new game? (1/2)")
        if i=="1":
            #list files in directory
            self.load()
        elif i=="2":
            #generate new game
            pass

        def validInp(text, val):
            value = input(text)
            gameEvents = {"t": GameFinish, "u": Undo, "r": Redo, "s": Save } #use a dictionary to avoid long if statements
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
                if self.Game.checkComplete():
                    print("Well done! Game complete")
                    prompt = input("Would you like to delete your game file? (y/n)")
                    if prompt.lower() !=  "n":
                        self.Game.deleteGame()
                else:
                    print("Incorrect")
                playAgain = input("\nPlay Again? (y/n): ").lower()
                if playAgain=="n":
                    self._gameOver = True
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

class GUI(UI):
    def __init__(self, file=None):
        super().__init__(file)

if __name__ == "__main__":
    Terminal("TestCaseGame.json").run()