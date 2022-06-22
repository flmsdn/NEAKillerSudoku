from Game import Game

class UI():
    def __init__(self):
        pass

    def play(self):
        raise NotImplementedError
    
    def display(self):
        raise NotImplementedError

class Terminal(UI):
    def __init__(self,file=None):
        self.__file = file

    def play(self):
        self.Game = Game(self.__file)
        while True:
            self.display()
            if self.Game.checkFull():
                if self.Game.checkComplete():
                    print("Well done! Game complete")
                    break
                else:
                    print("Incorrect")
            row,col,val = int(input("Row to input: ")), int(input("Column to input: ")), int(input("Value: "))
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
    def __init__(self):
        pass

if __name__ == "__main__":
    Terminal("TestCaseGame.json").play()