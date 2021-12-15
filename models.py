import sqlite3
import uuid, time
from datetime import datetime

class dbQuery():
    def __init__(self, db, mdb):
        self.db = db
        self.mdb = mdb
        self.con = sqlite3.connect(self.db, timeout=60)
        self.mCon = sqlite3.connect(self.mdb, timeout=60)
    
    #: Add the user into the database if not registered
    def setAccount(self, userId, userName=None):
        chatType = 'users' if userId > 0 else 'groups'
        con = self.con
        cur = con.cursor()

        isRegistered = self.isRegistered(userId, chatType)

        if not isRegistered:
            if chatType == 'users':
                cur.execute(f"Insert into {chatType} (userId, date) values ({userId}, \"{datetime.today().strftime('%Y-%m-%d')}\")")
                cur.execute(f'Insert into flood (ownerId) values ({userId})')

            else:
                cur.execute(f"Insert into {chatType} (userId, userName, date) values ({userId}, \"{userName}\", \"{datetime.today().strftime('%Y-%m-%d')}\")")
            
            cur.execute(f'Insert into settings (ownerId) values ({userId})')
                        
            con.commit()
        
        return isRegistered

    #: Find if a user is registered or not
    def isRegistered(self, userId, chatType='users'):
        con = self.con
        cur = con.cursor()

        isRegistered = cur.execute(f'SELECT * FROM {chatType} WHERE userId={userId}').fetchone()
        con.commit()

        return True if isRegistered else False

    #: Get all the registered users
    def getAllUsers(self, type='users', date=None, countOnly=False):
        con = self.con
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        if countOnly:
            if date:
                users = cur.execute(f'SELECT count(*) FROM {type} WHERE DATE="{date}"').fetchone()
            else:
                users = cur.execute(f'SELECT count(*) FROM {type}').fetchone()

        else:
            users = cur.execute(f'SELECT userId FROM {type}').fetchall()
        
        con.commit()
        return users
    
    #: Get all users exclude certain languages
    #: languages must inside a list
    def getUsersExcept(self, languages):
        con = self.con
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        users = cur.execute(f"SELECT ownerId FROM settings WHERE language NOT IN {str(languages).replace('[','(').replace(']',')')}").fetchall()
        con.commit()

        return users
    
    #: Get users of particular language
    def getUsers(self, language, countOnly=False):
        con = self.con
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        
        if countOnly:
            users = cur.execute(f'SELECT count(*) FROM settings WHERE language="{language}"').fetchone()
        else:
            users = cur.execute(f'SELECT ownerId FROM settings WHERE language="{language}"').fetchall()
        
        con.commit()
        return users

    #: Get the user's settings
    def getSetting(self, userId, var, table='settings'):
        self.setAccount(userId)
        con = self.con
        cur = con.cursor()
        
        setting = cur.execute(f'SELECT {var} FROM {table} WHERE ownerId={userId} limit 1').fetchone()
        con.commit()

        return setting[0] if setting else None

    #: Set the user's settings    
    def setSetting(self, userId, var, value, table='settings'):
        self.setAccount(userId)
        con = self.con
        cur = con.cursor()

        #!? If value is None, put value as NULL else "{string}"
        value = f'"{value}"' if value else 'NULL'
        cur.execute(f'INSERT OR IGNORE INTO {table} (ownerId, {var}) VALUES ({userId}, {value})')
        cur.execute(f'UPDATE {table} SET {var}={value} WHERE ownerId={userId}')
        con.commit()

    #: Set magnet link in the database
    def setMagnet(self, magnetLink):
        con = self.mCon
        cur = con.cursor()

        key = cur.execute(f'select key from data where magnetLink="{magnetLink}"').fetchone()
        key = key[0] if key else None

        if not key:
            key = uuid.uuid4().hex
            cur.execute(f'Insert into data (key, date, magnetLink) VALUES ("{key}", {int(time.time())}, "{magnetLink}")')
            con.commit()

        return key