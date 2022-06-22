import UI
import sys

def main():
    if len(sys.argv)>1:
        if sys.argv[1]=="t":
            userInterface = UI.Terminal()
        elif sys.argv[1]=="g":
            userInterface = UI.GUI()
        userInterface.play()
    else:
        userInterface = UI.Terminal()
        userInterface.play()


if __name__ == "__main__":
    main()