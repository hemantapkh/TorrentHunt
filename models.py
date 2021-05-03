import sqlite3

class dbQuery():
    def __init__(self, db):
        self.db = db
    
    #: Return the userId of the user. Returns None if the user is not registered.
    def getUserId(self, telegramId):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            user = cur.execute(f'SELECT * FROM users WHERE telegramId={telegramId}').fetchone()
            con.commit()
            
            return user[0] if user!=None else None

    #: Add the user into the database and give them a unique UserId
    def setUserId(self, telegramId):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            cursor.execute(f'Insert into users (telegramId) values ({telegramId})')
            con.commit()

    #: Get all the registered users
    def getAllAccounts(self):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            users = cur.execute(f'SELECT * FROM users WHERE telegramId NOT NULL').fetchall()
            con.commit()

            return users if users else None

    #: Get the user's settings
    def getSetting(self, userId, var):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()
            setting = cur.execute(f'SELECT {var} FROM settings WHERE ownerId={userId} limit 1').fetchone()
            con.commit()

            return setting[0] if setting!=None else None

    #: Set the user's settings    
    def setSetting(self, userId, var, value):
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()

            #!? If value is None, put value as NULL else "{string}"
            value = f'"{value}"' if value else 'NULL'
            cur.execute(f'INSERT OR IGNORE INTO settings (ownerId, {var}) VALUES ({userId}, {value})')
            cur.execute(f'UPDATE settings SET {var}={value} WHERE ownerId={userId}')
            con.commit()