from Game import Game

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

    def play(self):
        self.Game = Game(self._file)
        def validInp(text):
            value = int(input(text))
            if not 0<value<10:
                raise ValueError
            else:
                return value
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
                    row,col,val = validInp("Row to input: "), validInp("Column to input: "), validInp("Value: ")
                    break
                except:
                    print("Please input a valid number (between 1 and 9 inclusive)\n")
            print("\n")
            self.Game.updateCell(row-1,col-1,val)

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