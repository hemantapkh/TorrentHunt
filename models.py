import sqlite3

class dbQuery():
    def __init__(self, db):
        self.db = db
    
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
        
        users = cur.execute(f'SELECT * FROM users WHERE userId NOT NULL').fetchall()
        con.commit()

        return users if users else None
    
    #: Get users of particular language
    def getUsers(self, language):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        users = cur.execute(f'SELECT ownerId FROM settings WHERE language="{language}"').fetchall()
        con.commit()

        return users if users else None

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