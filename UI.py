from Game import Game

class GameFinish(Exception):
    pass

class UI():
    def __init__(self,file=None):
        self._file = file
        self._gameOver = False

    def run(self):
        while not self._gameOver:
            self.play()

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
            if value.lower() == "s":
                self._gameOver = True
                raise GameFinish
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
                    print("Game Stopped")
                    return
                except:
                    print("Please input a valid number (between 1 and 9 inclusive)\n")
            print("\n")
            self.Game.updateCell(x-1,y-1,val)

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