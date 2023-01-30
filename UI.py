import os, sys
import tkinter as tk
import tkinter.font, tkinter.messagebox
import winsound
import re
from Database import DBManager
from Settings import SettingsManager
from Game import Game
from Colours import Colour
from GUIGame import GUIGame

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
###########################################################
#
# CATEGORY A SKILL: Use of Complex OOP
# The UI class acts as a Base class that GUI and Terminal will inherit from with protected properties
# This allows for polymorphism with functions like 'display' working differently in the Terminal and GUI
#
###########################################################
    def __init__(self,loadOption=0):
        self._gameOver = False
        self._actionStack = []
        self._redoStack = []
        self._Game = Game()

    #loop the game playing
    def run(self):
        while not self._gameOver:
            self.play()
    
    #control a move being played
    def _playMove(self,x,y,val):
        action = Action(x,y,self._Game.getCell(x-1,y-1),val)
        self._Game.updateCell(x-1,y-1,val)
        self._actionStack.append(action)
        self._redoStack = []

###########################################################
#
# CATEGORY A SKILL: Stack Operations
# Use of Stack Operations to store Actions to Undo and Redo in the game
#
###########################################################
    def _undo(self):
        if not self._actionStack: return False
        action = self._actionStack.pop()
        self._redoStack.append(action)
        self._Game.updateCell(action.x-1,action.y-1,action.before)
        return True

    #redo move
    def _redo(self):
        if not self._redoStack: return False
        action = self._redoStack.pop()
        self._actionStack.append(action)
        self._Game.updateCell(action.x-1,action.y-1,action.after)
        return True
    
    #save the current game to a game file
    def _save(self,fileName,errors=0):
        if not fileName: return
        if len(fileName)>4 and fileName[-5:]!=".json":
            fileName+=".json"
        elif len(fileName)<5:
            fileName+=".json"
        self._Game.saveGame(fileName,errors)

    #load a game from a game file
    def _load(self, fileName):
        if len(fileName)>4 and fileName[-5:]!=".json":
            fileName+=".json"
        elif len(fileName)<5:
            fileName+=".json"
        self._actionStack = []
        self._Game.loadGame(fileName)

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
###########################################################
#
# CATEGORY A SKILL: Complex OOP
# The Terminal uses the UI class as the base for many of its methods
#
###########################################################
    def __init__(self, file=None):
        super().__init__(file)

    #shows the start screen, starts the game when given user input
    def run(self):
        print(Colour.GREEN+Colour.BOLD+"Sudoku"+Colour.ENDC+"\n")
        print(open(sys.path[0]+"\\Resources\\Instructions.txt").read(),"\n\nPress Enter to Play")
        input()
        super().run()

    #saves a file given a filename by the user
    def _save(self, fileName=None):
        if fileName is None:
            fileName = input("Enter a name to save the file as (leave blank to not save):")
        super()._save(fileName)
        print("Saved\n")

    #loads a file given a file name by the user
    def _load(self,fileName=None):
        if fileName is None:
            games = os.listdir(sys.path[0]+"\\LocalGames")
            print("   ".join(games))
            fileName = input("Choose a file to load: ")
        super()._load(fileName)

    #tells the user that the game is finished if the game has been completed
    def __gridComplete(self):
        if self._Game.checkComplete():
            print("Well done! Game complete")
            if self._Game.getFile:
                prompt = input("Would you like to delete your game file? (y/n)")
                if prompt.lower() !=  "n":
                    self._Game.deleteGame()
        else:
            print("Incorrect")
        playAgain = input("\nPlay Again? (y/n): ").lower()
        if playAgain=="n":
            self._gameOver = True

    #opens a game and then plays it
    def play(self):
        i = input("Would you like to load a game or play a new game? (1/2)")
        if i=="1":
            #load game
            self._load()
        elif i=="2":
            #generate new game
            try:
                diff = int(input("Input a difficulty 1-7 (2 is default): "))
                if not 0<diff<8: raise ValueError
            except:
                diff = 2
            self._Game.newGame(diff,0)

        #input validation
        def validInp(text, val):
            value = input(text)
            #use a dictionary to avoid long if statements
            gameEvents = {"t": GameFinish, "u": Undo, "r": Redo, "s": Save, "f": Solve, "l": Load }
            if value.lower() in gameEvents:
                raise gameEvents[value.lower()]
            minValue = -1 if val else 0
            if not minValue<int(value)<10:
                raise ValueError
            else:
                return int(value)
        
        while True:
            self.display()
            if self._Game.checkFull():
                self.__gridComplete()
                break
            while True:
                try:
                    x = validInp("Col to input ("+Colour.BLUE+Colour.BOLD+"x" +Colour.ENDC+ " coordinate): ",False)
                    y = validInp("Row to input ("+Colour.RED+Colour.BOLD+"y" +Colour.ENDC+" coordinate): ",False)
                    val = validInp("Value: ",True)
                    if self._Game.checkCell(x-1,y-1):
                        break
                    else:
                        raise ValueError
                except GameFinish:
                    prompt = input("Do you want to save your game first? (y/n)")
                    if prompt.lower()=="y":
                        self._save()
                    self._gameOver = True
                    print("Game Terminated")
                    return
                except Undo:
                    if self._undo():
                        print("Action Undone")
                        self.display()
                    else:
                        print("There were no moves to Undo")
                except Redo:
                    if self._redo():
                        print("Action Redone")
                        self.display()
                    else:
                        print("There were no moves to Redo")
                except Save:
                    self._save()
                except Load:
                    prompt = input("Do you want to save your game first? (y/n)")
                    if prompt.lower()=="y":
                        self._save()
                    self._load()
                    self.display()
                except Solve:
                    prompt = input("Are you sure you want to solve the grid? (y/n)")
                    if prompt.lower()=="y":
                        self._Game.solve()
                        self.display()
                        self.__gridComplete()
                        return
                except:
                    print("Please input a valid number (between 1 and 9 inclusive)\n")
            print("\n")
            self._playMove(x,y,val)

    #displays the grid
    def display(self):
        if self._Game.getType() == 0:
            grid = self._Game.getGrid()
            printedGrid=Colour.BLUE+Colour.BOLD+"  123 456 789\n"+Colour.ENDC
            for row in range(9):
                printedGrid+=Colour.RED+Colour.BOLD+str(row+1)+" "+Colour.ENDC
                for col in range(9):
                    if grid[row][col]!=0:
                        if self._Game.checkCell(col,row):
                            printedGrid+=str(grid[row][col])
                        else:
                            printedGrid+=Colour.BOLD+str(grid[row][col])+Colour.ENDC
                    else:
                        printedGrid+=" "
                    if col in (2,5): printedGrid+=Colour.BOLD+"|"+Colour.ENDC
                if row in (2,5): printedGrid+="\n  "+Colour.BOLD+"-"*11+Colour.ENDC
                printedGrid+="\n"
            print(printedGrid)

# Graphical User Interface
class GUI(UI):
###########################################################
#
# CATEGORY A SKILL: Complex OOP
# Undo, Redo, Save and Load base UI functions can all be called through buttons in the GUI
#
###########################################################
    def __init__(self, file=None):
        super().__init__(file)
        self.__root = None
        self.__settingsWindow = None
        self.__dataBaseManager = DBManager()
        self.__settingsManager = SettingsManager()
        self.__theme = self.__settingsManager.getTheme(self.__settingsManager.getConfigTheme())
        self.__GUIGame = GUIGame(self.__theme)
        accountDetails = self.__settingsManager.getAccount()
        if accountDetails[0]!=None:
            self.__dataBaseManager.checkAccountLogin(*accountDetails)
        self.__errorCells = set()
        self.__errors = 0
        self.__themeStrings = []
        #get all of the theme names as non-camel case strings
        for themeSt in self.__settingsManager.getThemes():
            themeMatch = re.match("([a-z]*)([A-Z][a-z]*)?Theme",themeSt)
            self.__themeStrings.append(" ".join( [s.capitalize() for s in themeMatch.groups() if s!=None] ))
        self.__audioPath = sys.path[0]+"\\Resources\\Sounds\\"
        self.__soundPresets = ["Classic","Retro","Bubbly"]
        self.__audioPreset = self.__settingsManager.getConfigAudio()
        self.__soundsDict = {0:"Write.wav",1: "Win.wav",2: "Gameover.wav"}
        self.__gameModes = ["Sudoku", "Killer Sudoku"]
        self.__muted = self.__settingsManager.getMuted()

    #plays a sound given an ID
    def playSound(self,id):
        if self.__muted: return
        winsound.PlaySound(self.__audioPath+self.__audioPreset+self.__soundsDict[id], winsound.SND_ASYNC | winsound.SND_ALIAS)

    #creates the GUI window and start menu
    def __startMenu(self):
        self.__root = tk.Tk()
        self.__font = tkinter.font.nametofont("TkDefaultFont")
        self.__font.configure(family="Verdana", size=14, weight=tkinter.font.NORMAL)
        self.__root.title("Main Menu")
        self.__root.state("zoomed")
        bgCol = self.__GUIGame.rgbToHex(self.__theme["background"])
        txtCol = self.__GUIGame.rgbToHex(self.__theme["line"])
        self.__root.configure(bg = bgCol)
        self.__dim = [self.__root.winfo_screenwidth(),self.__root.winfo_screenheight()]
        titleFrame = tk.Frame(self.__root, bg=bgCol)
        titleFrame.place(x=round(self.__dim[0]*0.45),y=round(self.__dim[1]*0.1),width=round(self.__dim[0]*0.1))
        titleText = tk.Label(titleFrame, text="Sudoku",fg=txtCol, bg=bgCol, font=("Sitka Text",26,"bold"), justify=tk.CENTER)
        titleText.pack(expand=True,fill=tk.X)
        buttonWidth = round(self.__dim[0]*0.1)
        buttonHeight = round(self.__dim[0]*0.02)
        offsetHoriz = round(self.__dim[0]*0.01)
        offsetVert = round(self.__dim[0]*0.2)
        #play
        playFrame = tk.Frame(self.__root)
        playFrame.place(x=self.__dim[0]//2-buttonWidth-offsetHoriz,y=offsetVert,width=buttonWidth,height=buttonHeight)
        playButton = tk.Button(playFrame,text="Play", command=self.playRandom,fg=txtCol, bg=bgCol)
        playButton.pack(expand=True,fill=tk.BOTH)
        #load
        loadFrame = tk.Frame(self.__root)
        loadFrame.place(x=self.__dim[0]//2+offsetHoriz,y=offsetVert,width=buttonWidth,height=buttonHeight)
        loadButton = tk.Button(loadFrame,text="Load", command=self.playLoad,fg=txtCol, bg=bgCol)
        loadButton.pack(expand=True,fill=tk.BOTH)
        games = os.listdir(sys.path[0]+"\\LocalGames")
        gameNames = []
        for fileName in games:
            m = re.match(r"(.*)\.json",fileName)
            if m.groups(): gameNames.append(m.groups()[0])
        self.__gameOption = tk.StringVar()
        self.__gameOption.set(gameNames[0])
        optionDropDown = tk.OptionMenu(self.__root,self.__gameOption,*gameNames)
        optionDropDown.config(bg=bgCol,fg=txtCol)
        optionDropDown["menu"].config(bg=bgCol,fg=txtCol)
        optionDropDown.place(x=self.__dim[0]//2+offsetHoriz,y=offsetVert+round(self.__dim[1]*0.05))
        #quit
        quitFrame = tk.Frame(self.__root)
        quitFrame.place(x=round(self.__dim[0]*0.95)-buttonWidth,y=round(self.__dim[1]*0.92)-buttonHeight,width=buttonWidth,height=buttonHeight)
        quitButton = tk.Button(quitFrame,text="Quit", command=self.gameOver,fg=txtCol, bg=bgCol)
        quitButton.pack(expand=True,fill=tk.BOTH)
        #settings
        settingsFrame = tk.Frame(self.__root)
        settingsFrame.place(x=round(self.__dim[0]*0.95)-buttonWidth,y=round(self.__dim[1]*0.08),width=buttonWidth,height=buttonHeight)
        settingsButton = tk.Button(settingsFrame,text="Settings",command=self.__openSettingsWindow,fg=txtCol, bg=bgCol)
        settingsButton.pack(expand=True,fill=tk.BOTH)
        #difficulty slider
        sliderFrame = tk.Frame(self.__root, bg=bgCol)
        sliderFrame.place(x=self.__dim[0]//2-buttonWidth-offsetHoriz,y=offsetVert+round(self.__dim[1]*0.05),width=buttonWidth,height=buttonHeight*4)
        self.__selectedGameMode = tk.StringVar()
        self.__selectedGameMode.set(self.__gameModes[0])
        gameModeSelect = tk.OptionMenu(sliderFrame, self.__selectedGameMode, *self.__gameModes)
        gameModeSelect.config(bg=bgCol,fg=txtCol)
        gameModeSelect["menu"].config(bg=bgCol,fg=txtCol)
        gameModeSelect.pack()
        text = tk.Label(sliderFrame, text="Difficulty: ",fg=txtCol, bg=bgCol)
        text.pack()
        self.__difficultySlider = tk.Scale(sliderFrame, from_=1, to=7, orient=tk.HORIZONTAL,fg=txtCol, bg=bgCol,relief="flat",highlightthickness=0)
        self.__difficultySlider.pack(expand=True,fill=tk.X)

    #plays a move and finds any potential errors
    def _playMove(self, x, y, val):
        super()._playMove(x, y, val)
        self.__errorCells = self._Game.getErrorCells()

    #opens the settings window
    def __openSettingsWindow(self):
        if self.__GUIGame.gameWindow!=None: #make sure game is not open at same time as settings window
            if not self.__GUIGame.gameWindow.winfo_exists():
                self.__GUIGame.gameWindow = None
            else:
                return
        #create the window
        self.__settingsWindow = tk.Toplevel()
        self.__settingsWindow.title("Settings")
        self.__settingsWindow.state("zoomed")
        self.__settingsWindow.configure(bg=self.__GUIGame.rgbToHex(self.__theme["background"]))
        dims = (self.__settingsWindow.winfo_screenwidth(),self.__settingsWindow.winfo_screenheight())
        self.__settingsWindow.geometry("%dx%d+0+0" % dims)
        frameHeight = round(dims[1]*0.03)
        bgCol = self.__GUIGame.rgbToHex(self.__theme["background"])
        txtCol = self.__GUIGame.rgbToHex(self.__theme["line"])
        #create the account log in and sign in frame
        self.__accountFrame = tk.Frame(self.__settingsWindow,width=dims[0],height=round(dims[1]*0.23),bg=bgCol)
        self.__accountFrame.pack()
        inputFrameU = tk.Frame(self.__accountFrame,bg=bgCol)
        inputFrameU.place(x=round(dims[0]*0.5),y=round(dims[1]*0.10),width=round(dims[0]*0.1),height=frameHeight)
        textFrameU = tk.Frame(self.__accountFrame,bg=bgCol)
        textFrameU.place(x=round(dims[0]*0.4),y=round(dims[1]*0.10),width=round(dims[0]*0.1),height=frameHeight)
        inputFrameP = tk.Frame(self.__accountFrame,bg=bgCol)
        inputFrameP.place(x=round(dims[0]*0.5),y=round(dims[1]*0.10)+frameHeight,width=round(dims[0]*0.1),height=frameHeight)
        textFrameP = tk.Frame(self.__accountFrame,bg=bgCol)
        textFrameP.place(x=round(dims[0]*0.4),y=round(dims[1]*0.10)+frameHeight,width=round(dims[0]*0.1),height=frameHeight)
        self.__logInInputs = [None]*4
        #username row
        self.__logInInputs[0] = tk.Entry(inputFrameU)
        usernameText = tk.Label(textFrameU,text="Username:",bg=bgCol,fg=txtCol)
        usernameText.pack(side=tk.RIGHT,anchor=tk.NE)
        self.__logInInputs[0].pack(side=tk.LEFT,anchor=tk.NW)
        #password
        self.__logInInputs[1] = tk.Entry(inputFrameP,show="*")
        passwordText = tk.Label(textFrameP,text="Password:",bg=bgCol,fg=txtCol)
        passwordText.pack(side=tk.RIGHT,anchor=tk.E)
        self.__logInInputs[1].pack(side=tk.LEFT)
        #buttons
        logInFrame = tk.Frame(self.__accountFrame,bg=bgCol)
        logInFrame.place(x=round(dims[0]*0.5),y=round(dims[1]*0.20),width=round(dims[0]*0.1),height=frameHeight)
        signUpFrame = tk.Frame(self.__accountFrame,bg=bgCol)
        signUpFrame.place(x=round(dims[0]*0.4),y=round(dims[1]*0.20),width=round(dims[0]*0.1),height=frameHeight)
        self.__logInInputs[2] = tk.Button(logInFrame,text="Log In",command=self.__attemptLogin,bg=bgCol,fg=txtCol)
        self.__logInInputs[3] = tk.Button(signUpFrame,text="Create Account",command=self.__attemptSignUp,bg=bgCol,fg=txtCol)
        self.__logInInputs[3].pack(fill=tk.BOTH,expand=True)
        self.__logInInputs[2].pack(fill=tk.BOTH,expand=True)
        #account stats
        self.__statsFrame = tk.Frame(self.__settingsWindow,bg=bgCol)
        if self.__dataBaseManager.checkLoggedIn():
            #only create the account stats if you are logged in
            accStats = self.__dataBaseManager.getAccountStats()
            self.__statsFrame.place(x=round(dims[0]*0.3),y=round(dims[1]*0.23),width=round(dims[0]*0.4),height=frameHeight)
            statsLabel = tk.Label(self.__statsFrame, text=f"Solved games: {accStats[0]}, Average solve time: {accStats[1]:.1f}",bg=bgCol,fg=txtCol)
            statsLabel.pack(expand=True, fill=tk.BOTH)
        #settings menu underneath
        settingsMenu = tk.Frame(self.__settingsWindow,width=dims[0],height=round(dims[1]*0.70),bd=1, relief="groove",bg=bgCol)
        settingsMenu.place(x=0,y=round(dims[1]*0.28),width=dims[0],height=round(dims[1]*0.72))
        settingsText = tk.Label(settingsMenu,text="Settings",justify=tk.CENTER, font=("Helvetica",15,"bold"), width=round(dims[0]*0.2),bg=bgCol,fg=txtCol)
        settingsText.pack(fill=tk.X)
        #colour customisation
        self.__themeOption = tk.StringVar()
        self.__themeOption.set(self.__themeStrings[self.__settingsManager.getConfigTheme()])
        themeDropDown = tk.OptionMenu(settingsMenu,self.__themeOption,*self.__themeStrings)
        themeDropDown.config(bg=bgCol,fg=txtCol)
        themeDropDown["menu"].config(bg=bgCol,fg=txtCol)
        themeDropDown.pack()
        themeSelectButton = tk.Button(settingsMenu, text="Update Theme",bg=bgCol,fg=txtCol,command=self.__updateTheme)
        themeSelectButton.pack()
        #sound customisation
        self.__audioOption = tk.StringVar()
        self.__audioOption.set(self.__audioPreset.capitalize())
        audioDropDown = tk.OptionMenu(settingsMenu,self.__audioOption,*self.__soundPresets)
        audioDropDown.config(bg=bgCol,fg=txtCol)
        audioDropDown["menu"].config(bg=bgCol,fg=txtCol)
        audioDropDown.pack()
        audioSelectButton = tk.Button(settingsMenu, text="Update Audio Preset",bg=bgCol,fg=txtCol,command=self.__updateAudio)
        audioSelectButton.pack()
        #mute button
        self.__muteButton = tk.Button(settingsMenu,text=("Mute","Unmute")[self.__muted],command=self.__toggleMute,bg=bgCol,fg=txtCol)
        self.__muteButton.pack()
        #Sign out button
        signOutFrame = tk.Frame(self.__settingsWindow,bg=bgCol)
        signOutFrame.place(x=round(dims[0]*0.75),y=round(dims[1]*0.75),width = round(dims[1]*0.15), height= round(dims[1]*0.05))
        signOutButton = tk.Button(signOutFrame, text="Sign Out", command=self.__attemptSignOut,bg=bgCol,fg=txtCol)
        signOutButton.pack(expand=True,fill=tk.BOTH)
        quitFrame = tk.Frame(self.__settingsWindow,bg=bgCol)
        quitFrame.place(x=round(dims[0]*0.75),y=round(dims[1]*0.85),width = round(dims[1]*0.15), height= round(dims[1]*0.05))
        quitButton = tk.Button(quitFrame, text="Close", command=self.__closeSettings,bg=bgCol,fg=txtCol)
        quitButton.pack(expand=True,fill=tk.BOTH)
        #this needs to be last for layering
        if self.__dataBaseManager.checkLoggedIn():
            self.__logInMessage = tk.Label(self.__settingsWindow, text="Logged in as " + self.__dataBaseManager.getUsername(),bg=bgCol,fg=txtCol)
            self.__updateLoginInputs()
            self.__logInMessage.place(x=round(dims[0]*0.2),y=round(dims[1]*0.03),width=round(dims[0]*0.2),height=round(dims[1]*0.1))
        else:
            self.__logInMessage = tk.Label(self.__settingsWindow,bg=bgCol,fg=txtCol)
            self.__logInMessage.place(x=round(dims[0]*0.2),y=round(dims[1]*0.03),width=round(dims[0]*0.2),height=round(dims[1]*0.1))

    #mutes or unmutes the game
    def __toggleMute(self):
        self.__settingsManager.toggleMute()
        self.__muted = self.__settingsManager.getMuted()
        self.__muteButton.config(text=("Mute","Unmute")[self.__muted])

    #updates the current Colour Theme
    def __updateTheme(self):
        ind = self.__themeStrings.index(self.__themeOption.get())
        self.__settingsManager.setTheme(ind)
        tkinter.messagebox.showinfo("Restart Game", "Restart needed for Theme to update")
        self.__closeSettings()
        self.__openSettingsWindow()
    
    #updates the current Audio Preset
    def __updateAudio(self):
        self.__audioPreset = self.__audioOption.get().lower()
        self.__settingsManager.setAudio(self.__audioPreset)

    #updates the GUI to show an update password button
    def __updateLoginInputs(self):
        self.__logInInputs[3].pack_forget()
        self.__logInInputs[2].config(text="Update Password", command=self.__updatePW)
    
    #allows the currently logged in user to update their password
    def __updatePW(self):
        if self.__dataBaseManager.updatePassword(*[a.get() for a in self.__logInInputs[:2]]):
            for a in self.__logInInputs[:2]: a.delete(0,tk.END)

    #attempts to log in to an account
    def __attemptLogin(self):
        successfulLogin = self.__dataBaseManager.attemptLogin(*[a.get() for a in self.__logInInputs[:2]])
        if successfulLogin:
            print("Logged in")
            for a in self.__logInInputs[:2]: a.delete(0,tk.END)
            self.__settingsManager.updateAccount(*self.__dataBaseManager.getAccountDetails())
            dims = (self.__settingsWindow.winfo_screenwidth(),self.__settingsWindow.winfo_screenheight())
            self.__closeSettings()
            self.__openSettingsWindow()
            self.__logInMessage.config(text="Logged in as " + self.__dataBaseManager.getUsername())
            self.__logInMessage.place(x=round(dims[0]*0.2),y=round(dims[1]*0.03),width=round(dims[0]*0.2),height=round(dims[1]*0.1))
    
    #attempts to create a new account
    def __attemptSignUp(self):
        successfulSignUp = self.__dataBaseManager.attemptSignUp(*[a.get() for a in self.__logInInputs[:2]])
        if successfulSignUp:
            print("Successfully signed up")
            self.__dataBaseManager.attemptLogin(*[a.get() for a in self.__logInInputs[:2]])
            for a in self.__logInInputs[:2]: a.delete(0,tk.END)
            dims = (self.__settingsWindow.winfo_screenwidth(),self.__settingsWindow.winfo_screenheight())
            self.__updateLoginInputs()
            self.__logInMessage.config(text="Logged in as " + self.__dataBaseManager.getUsername())
            self.__logInMessage.place(x=round(dims[0]*0.2),y=round(dims[1]*0.1),width=round(dims[0]*0.2),height=round(dims[1]*0.1))

    #attempts to sign out of the current account
    def __attemptSignOut(self):
        if self.__dataBaseManager.checkLoggedIn():
            self.__settingsManager.updateAccount(None,None) #signs out in the settings
            self.__dataBaseManager.signOut()
            #put the account login back in place
            self.__closeSettings()
            self.__openSettingsWindow()
            print("Signed Out")
        else:
            print("You are already signed out")

    #closes the settings window
    def __closeSettings(self):
        self.__settingsWindow.destroy()
        self.__settingsWindow = None

    #opens up a window for the game to be played in
    def __gameScreen(self):
        if self.__settingsWindow!=None:
            if not self.__settingsWindow.winfo_exists():
                self.__settingsWindow=None
            else:
                return #stop the game opening when the settings window is open
        self.__GUIGame.openWindow(self.saveButton,self.loadButton,self.closeGame,self.undoButton,self.redoButton,self.solveButton,self.toggleWriteButton)
        self.eventSetup()
        self.__GUIGame.startGame()

    #updates the Pen/Pencil button
    def toggleWriteButton(self):
        self.__GUIGame.updateWriteMode()
        self._Game.toggleWrite()

    #closes the current game
    def closeGame(self):
        self.__GUIGame.closeGame()
    
    #methods handling events
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
        self.__GUIGame.updateWriteMode()
        self._Game.toggleWrite()

    #creates a new game of the chosen difficulty
    def playRandom(self):
        self._Game.newGame(self.__difficultySlider.get(),gameType = self.__gameModes.index(self.__selectedGameMode.get()))
        self.__errorCells = self._Game.getErrorCells()
        self.__errors = 0
        self.__gameScreen()
    
    #plays a game that the user has loaded
    def playLoad(self):
        self.loadButton(play=True)
        self.__gameScreen()

    #handles button inputs
    def undoButton(self):
        if self.__GUIGame.gameComplete(): return
        if super()._undo():
            self.__errorCells = self._Game.getErrorCells()
            self.display()

    def redoButton(self):
        if super()._redo():
            self.display()

    def solveButton(self):
        self._Game.solve()
        self.__GUIGame.endGame()
        self.display()
        
    def loadButton(self, play=False):
        if play:
            value=self.__gameOption.get()
            super()._load(value)
            self.__errorCells = self._Game.getErrorCells()
            self.__errors = self._Game.getErrors()
            return
        fileName = self.__GUIGame.loadPrompt()
        if fileName:
            super()._load(fileName)
            self.__GUIGame.resetGame()
            self.__errorCells = self._Game.getErrorCells()
            self.__errors = self._Game.getErrors()
            self.display()

    def saveButton(self):
        fileName = self.__GUIGame.savePrompt()
        super()._save(fileName,self.__errors)

    def clickCanvas(self,event):
        if self.__GUIGame.gameComplete(): return
        self.__GUIGame.cellClick(event)
        self.display()

    #binds all mouse and keyboard events
    def eventSetup(self):
        self.__GUIGame.gameGrid.bind("<Button 1>",self.clickCanvas)
        for number in range(1,10):
            self.__GUIGame.gameWindow.bind(str(number),self.__numInput)
        self.__GUIGame.gameWindow.bind("<Key-BackSpace>",self.__numInput)
        gameEvents = {"t": self.closeGame, "u": self.undo, "r": self.redo, "s": self.save, "f": self.solve, "p": self.toggleWrite }
        for x in gameEvents:
            self.__GUIGame.gameWindow.bind(x,gameEvents[x])
        self.__GUIGame.gameWindow.bind("<Configure>",self.resize)

    #resizes the game window
    def resize(self,event):
        self.__GUIGame.resize(event)
        self.display()

    #handles numerical input
    def __numInput(self,event):
        if self.__GUIGame.gameComplete(): return
        if event.keycode==8:
            cell = self.__GUIGame.getSelected()
            if self._Game.checkCell(cell[0],cell[1]):
                self._playMove(cell[0]+1,cell[1]+1,0)
                self.display()
        err = self.__errorCells
        if 48<event.keycode<58:
            value = event.keycode-48
            cell = self.__GUIGame.getSelected()
            if self._Game.checkCell(cell[0],cell[1]):
                self._playMove(cell[0]+1,cell[1]+1,value)
                #play sound
                self.playSound(0)
                if self.__errorCells!=err and self.__errorCells:
                    self.__errors+=1
                    if self.__errors>2:
                        self.__GUIGame.gameOver()
                        self.playSound(2)
                if self._Game.checkFull():
                    if self._Game.checkComplete():
                        timeTaken = self._Game.getTime() #get time taken to add to the account statistics
                        self.__dataBaseManager.addGame(True,timeTaken)
                        self.__GUIGame.endGame()
                        self.playSound(1)
                self.display()

    #runs the GUI as a whole
    def run(self):
        self.__startMenu()
        self.__root.mainloop()

    #updates the GUI grid
    def display(self):
        gridArr, fCells, errCells, errs, pMarkings = self._Game.getGrid(),self._Game.fixedCells(),self.__errorCells,self.__errors,self._Game.getPencilMarkings()
        if self._Game.getType()==0:
            self.__GUIGame.updateGrid(gridArr, fCells, errCells, errs, pMarkings)
        elif self._Game.getType()==1:
            self.__GUIGame.updateGrid(gridArr, fCells, errCells, errs, pMarkings, self._Game.getCages(), self._Game.getCagesDict())
    
    #closes the entire game
    def gameOver(self):
        self.gameOver = True
        self.__root.destroy()
        self.__root = None

if __name__ == "__main__":
    pass