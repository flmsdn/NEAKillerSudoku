import sys
import sqlite3
import hashlib

class DBManager():
    def __init__(self):
        self.__loggedInAccount = None #if an account is logged in then this is the account name, otherwise the account data cannot be accessed
        self.initialiseConnection()

    #creates the initial database connection
    def initialiseConnection(self):
        path = sys.path[0]+"\\Resources\\Accounts.db"
        self.__connection = sqlite3.connect(path)
        self.__cur = self.__connection.cursor()
        print("Connected to Database")
        checkTable = """SELECT name FROM sqlite_master WHERE type='table' AND name='accounts' """
        self.__cur.execute(checkTable)
        if self.__cur.fetchone()==None:
            #table doesn't exist, database is new so create the table
            self.__createAccountsTable()

    #creates the accounts table in the database
    def __createAccountsTable(self):
        tableCreation = """CREATE TABLE IF NOT EXISTS accounts
        (accid INTEGER PRIMARY KEY,
         name           TEXT    NOT NULL,
         pwhash            CHAR(64)     NOT NULL,
         solvedGames        INT,
         solveTime         REAL);"""
        self.__cur.execute(tableCreation)

    #tries to log in to an account with the given username and password
    def attemptLogin(self,username,password):
        pwHash = self.__hashPassword(password)
        #check if the password hash in the table is in the account
        return self.checkAccountLogin(username,pwHash)
    
    #checks if the hashed password matches the hash stored in the database
    def checkAccountLogin(self,username,pwHash):
        hashQuery = """SELECT pwhash FROM accounts WHERE name='"""+username+"'"
        res = self.__cur.execute(hashQuery)
        r=res.fetchone()
        if r: #check if hashes match and if so log in
            if r[0]==pwHash:
                self.__loggedInAccount=username #log in
                return True
        return False

    #tries to create an account with the given details
    def attemptSignUp(self,username,password): #Single table SQL query to add accounts
        pwHash = self.__hashPassword(password)
        #check if the password hash in the table is in the account
        hashQuery = """SELECT pwhash FROM accounts WHERE name='"""+username+"'"
        res = self.__cur.execute(hashQuery)
        r=res.fetchone()
        if r: #check if hashes match and if so log in
            if r[0]==pwHash:
                self.__loggedInAccount=username #log in
                print("Logged In")
                return True
        else:
            accountCreation = """INSERT INTO accounts (name, pwhash, solvedGames, solveTime) VALUES """ + str( (username,pwHash,0,0) )#create a new account in the table
            self.__cur.execute(accountCreation)
            self.__connection.commit()
            print("Account Created")
            return True
        return False

    #returns the currently logged in accounts username
    def getUsername(self):
        return self.__loggedInAccount
    
    #updates the account password
    def updatePassword(self,username,password):
        if username == self.__loggedInAccount:
            pwHash = self.__hashPassword(password)
            passwordUpdate = f"UPDATE accounts SET pwhash = '{pwHash}' WHERE name = '{username}'"
            self.__cur.execute(passwordUpdate)
            self.__connection.commit()
            print("Password Updated")
            return True
        return False

    #returns account details
    def getAccountDetails(self):
        hashQuery = """SELECT pwhash FROM accounts WHERE name='"""+self.__loggedInAccount+"'"
        res = self.__cur.execute(hashQuery)
        r=res.fetchone()
        if r: #check if hashes match and if so log in
            return (self.__loggedInAccount,r[0])
    
    def signOut(self):
        self.__loggedInAccount = None

    #returns a sha256 hash of the given password
    def __hashPassword(self,password):
        hashAlgorithm = hashlib.sha256()
        hashAlgorithm.update(password.encode("utf-8"))
        return hashAlgorithm.hexdigest()
    
    #returns whether the user is logged in
    def checkLoggedIn(self):
        if self.__loggedInAccount!=None:
            return True
        return False

    #returns all game statistics for the account
    def getAccountStats(self):
        if self.__loggedInAccount:
            statsQuery = """SELECT solvedGames, solveTime FROM accounts WHERE name='"""+self.__loggedInAccount+"'"
            res = self.__cur.execute(statsQuery)
            return res.fetchall()[0]
    
    #updates the account statistics to include a game
    def addGame(self,win,time = 0):
        if win and time>0 and self.__loggedInAccount: #only use stats if it is a win (we assume 0 seconds isn't possible)
            #get the current account stats
            solvedGames, solveTime = self.getAccountStats()
            solveTime *= solvedGames
            solvedGames += 1
            solveTime = (solveTime + time)/solvedGames #calculate new solvedGames and solveTime
            passwordUpdate = f"UPDATE accounts SET solvedGames = {solvedGames}, solveTime = {solveTime} WHERE name = '{self.__loggedInAccount}'"
            self.__cur.execute(passwordUpdate)
            self.__connection.commit()

if __name__=="__main__":
    dbm = DBManager()
    dbm.initialiseConnection()
