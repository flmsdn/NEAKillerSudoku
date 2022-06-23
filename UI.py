from multiprocessing import Event
from Game import Game

#Events are going to be used with Exception Handling
class GameFinish(Exception):
    pass

class Undo(Exception):
    pass

class Redo(Exception):
    pass

class Action():
    def __init__(self,x,y,before,after):
        self.x,self.y,self.before,self.after=x,y,before,after

class UI():
    def __init__(self,file=None):
        self._file = file
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
        print(open("Instructions.txt").read(),"\n\nPress Enter to Play")
        input()
        super().run()

    def play(self):
        self.Game = Game(self._file)

        def validInp(text):
            value = input(text)
            gameEvents = {"s": GameFinish, "u": Undo, "r": Redo } #use a dictionary to avoid long if statements
            if value.lower() in gameEvents:
                raise gameEvents[value.lower()]
            if not 0<int(value)<10:
                raise ValueError
            else:
                return int(value)
        
        while True:
            self.display()
            if self.Game.checkFull():
                if self.Game.checkComplete():
                    print("Well done! Game complete")
                else:
                    print("Incorrect")
                playAgain = input("\nPlay Again? (y/n): ").lower()
                if playAgain=="n":
                    self._gameOver = True
                break
            while True:
                try:
                    x,y,val = validInp("Col to input (x coordinate): "), validInp("Row to input (y coordinate): "), validInp("Value: ")
                    if self.Game.checkCell(x-1,y-1):
                        break
                    else:
                        raise ValueError
                except GameFinish:
                    self._gameOver = True
                    print("Game Stopped")
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
                        printedGrid+=str(grid[row][col])
                    else:
                        printedGrid+=" "
                    if col in (2,5): printedGrid+="|"
                if row in (2,5): printedGrid+="\n  "+"-"*11
                printedGrid+="\n"
            print(printedGrid)
        else:
            pass

class GUI(UI):
    def __init__(self, file=None):
        super().__init__(file)

if __name__ == "__main__":
    Terminal("TestCaseGame.json").run()