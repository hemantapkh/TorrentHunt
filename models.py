import sqlite3
import uuid, time

class dbQuery():
    def __init__(self, db, mdb):
        self.db = db
        self.mdb = mdb
    
    #: Add the user into the database if not registered
    def setAccount(self, userId):
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        isRegistered = cur.execute(f'SELECT * FROM users WHERE userId={userId}').fetchone()
        con.commit()

        isRegistered = True if isRegistered else False

        if not isRegistered:
            cur.execute(f'Insert into users (userId) values ({userId})')
            cur.execute(f'Insert into settings (ownerId) values ({userId})')
            con.commit()
        
        return isRegistered

    #: Get all the registered users
    def getAllUsers(self):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        users = cur.execute(f'SELECT userId FROM users').fetchall()
        con.commit()

        return users
    
    #: Get all users exclude certain languages
    #: languages must inside a list
    def getUsersExcept(self, languages):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        users = cur.execute(f"SELECT ownerId FROM settings WHERE language NOT IN {str(languages).replace('[','(').replace(']',')')}").fetchall()
        con.commit()

        return users
    
    #: Get users of particular language
    def getUsers(self, language):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        users = cur.execute(f'SELECT ownerId FROM settings WHERE language="{language}"').fetchall()
        con.commit()

        return users

    #: Get the user's settings
    def getSetting(self, userId, var):
        self.setAccount(userId)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        
        setting = cur.execute(f'SELECT {var} FROM settings WHERE ownerId={userId} limit 1').fetchone()
        con.commit()

        return setting[0] if setting else None

    #: Set the user's settings    
    def setSetting(self, userId, var, value):
        self.setAccount(userId)
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        #!? If value is None, put value as NULL else "{string}"
        value = f'"{value}"' if value else 'NULL'
        cur.execute(f'INSERT OR IGNORE INTO settings (ownerId, {var}) VALUES ({userId}, {value})')
        cur.execute(f'UPDATE settings SET {var}={value} WHERE ownerId={userId}')
        con.commit()

    #: Set magnet link in the database
    def setMagnet(self, magnetLink):
        con = sqlite3.connect(self.mdb)
        cur = con.cursor()

        key = cur.execute(f'select key from data where magnetLink="{magnetLink}"').fetchone()
        key = key[0] if key else None

        if not key:
            key = uuid.uuid4().hex
            cur.execute(f'Insert into data (key, date, magnetLink) VALUES ("{key}", {int(time.time())}, "{magnetLink}")')
            con.commit()

        return key