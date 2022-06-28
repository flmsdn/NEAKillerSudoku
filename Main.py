import UI
import sys

def usage():
    print("\nHow to use the game:\nIn the terminal, run the game file with 'python Main.py'\nFollow this with an argument 't' or 'g' to play in the Terminal or a GUI")

def main():
    #check if the file is being run with arguments
    if len(sys.argv)>1:
        if sys.argv[1]=="t":
            userInterface = UI.Terminal()
        elif sys.argv[1]=="g":
            userInterface = UI.GUI()
        else:
            #if an invalid argument is given, then show a prompt on how to use it 
            usage()
            return
        userInterface.run()
    else:
        #by default open a GUI game
        userInterface = UI.Terminal()
        userInterface.run()

if __name__ == "__main__":
    main()