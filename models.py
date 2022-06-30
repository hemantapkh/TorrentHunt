import uuid
import sqlite3
from datetime import datetime


class dbQuery():
    def __init__(self, db, mdb):
        self.db = db
        self.mdb = mdb

    #: Add the user into the database if not registered
    def setAccount(self, userId, userName=None, referrer=None):
        chatType = 'users' if userId > 0 else 'groups'
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        isRegistered = self.isRegistered(userId, chatType)

        if not isRegistered:
            if chatType == 'users':
                cur.execute(f'Insert into {chatType} (userId, date, referrer) values (?, ?, ?)', (userId, datetime.today().strftime('%Y-%m-%d'), referrer))
                cur.execute('Insert into flood (ownerId) values (?)', (userId,))

            else:
                cur.execute(f'Insert into {chatType} (userId, userName, date) values (?, ?, ?)', (userId, userName, datetime.today().strftime('%Y-%m-%d')))

            cur.execute('Insert into settings (ownerId) values (?)', (userId,))

            con.commit()

        return isRegistered

    #: Find if a user is registered or not
    def isRegistered(self, userId, chatType='users'):
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        isRegistered = cur.execute(f'SELECT * FROM {chatType} WHERE userId=?', (userId,)).fetchone()
        con.commit()

        return True if isRegistered else False

    #: Get all the registered users
    def getAllUsers(self, type='users', date=None, countOnly=False):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()

        if countOnly:
            if date:
                users = cur.execute(f'SELECT count(*) FROM {type} WHERE DATE=?', (date,)).fetchone()
            else:
                users = cur.execute(f'SELECT count(*) FROM {type}').fetchone()

        else:
            users = cur.execute(f'SELECT userId FROM {type}').fetchall()

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
    def getUsers(self, language, countOnly=False):
        con = sqlite3.connect(self.db)
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()

        if countOnly:
            users = cur.execute('SELECT count(*) FROM settings WHERE language=?', (language,)).fetchone()
        else:
            users = cur.execute('SELECT ownerId FROM settings WHERE language=?', (language,)).fetchall()

        con.commit()
        return users

    #: Get the user's settings
    def getSetting(self, userId, var, table='settings'):
        self.setAccount(userId)
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        setting = cur.execute(f'SELECT {var} FROM {table} WHERE ownerId=?', (userId,)).fetchone()
        con.commit()

        return setting[0] if setting else None

    #: Set the user's settings
    def setSetting(self, userId, var, value, table='settings'):
        self.setAccount(userId)
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        cur.execute(f'INSERT OR IGNORE INTO {table} (ownerId, {var}) VALUES (?, ?)', (userId, value))
        cur.execute(f'UPDATE {table} SET {var}=? WHERE ownerId=?', (value, userId))
        con.commit()

    #: Set magnet link in the database
    def setMagnet(self, hash, title, magnetLink):
        con = sqlite3.connect(self.mdb)
        cur = con.cursor()

        cur.execute(f'Insert OR IGNORE INTO data (hash, title, magnetLink) VALUES (?,?,?)', (hash, title, magnetLink))
        con.commit()

    #: Add item to the wishlist
    def addWishlist(self, ownerId, hash):
        con = sqlite3.connect(self.mdb)
        cur = con.cursor()

        id = cur.execute('SELECT wishlistId FROM wishlist WHERE hash=?', (hash,)).fetchone()

        if not id:
            key = str(uuid.uuid4().int)[:8]
            cur.execute('Insert INTO wishlist (wishlistId, ownerId, hash) VALUES (?,?,?)', (key, ownerId, hash))
            con.commit()
