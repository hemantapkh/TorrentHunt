import psycopg2
import uuid, time
from datetime import datetime

class dbQuery():
    def __init__(self, db, mdb):
        conn = psycopg2.connect(user="postgres", password="postgres", host="127.0.0.1", port="5432", database=db)
        conn.autocommit = True
        self.cur = conn.cursor()

        conn = psycopg2.connect(user="postgres", password="postgres", host="127.0.0.1", port="5432", database=mdb)
        conn.autocommit = True
        self.mcur = conn.cursor()

    #: Add the user into the database if not registered
    def setAccount(self, userId, userName=None):
        chatType = 'users' if userId > 0 else 'groups'

        self.cur.execute(f"""Insert into {chatType}
                        (userId, userName, date) values 
                        ({userId}, '{userName}', '{datetime.today().strftime("%Y-%m-%d")}')
                        ON CONFLICT (userId) DO UPDATE SET userId=EXCLUDED.userId 
                        RETURNING userId
                        """)

        isRegistered = self.cur.fetchone()
                        
        return True if isRegistered else False

    #: Get user stats
    def getUsers(self, type='users', language=None, languageExcept=None, date=None, countOnly=False):
        if countOnly:
            self.cur.execute(f"""SELECT count(*) FROM settings 
                                FULL OUTER JOIN USERS on ownerId=userId
                                WHERE
                                    language={f"'{language}'" if language else 'language'} AND
                                    date={f"'{date}'" if date else 'date'}
                                    {f"AND language NOT IN {str(languageExcept).replace('[','(').replace(']',')')}" if languageExcept else ''}  
            """)
            
            users = self.cur.fetchone()[0]
        
        else:
            self.cur.execute(f"""
                    SELECT userId FROM settings 
                    FULL OUTER JOIN USERS on ownerId=userId
                    WHERE
                        language={f"'{language}'" if language else 'language'} AND
                        date={f"'{date}'" if date else 'date'}
                        {f"AND language NOT IN {str(languageExcept).replace('[','(').replace(']',')')}" if languageExcept else ''} 
            """)
            
            users = self.cur.fetchall()

        return users

    #: Get the user's settings
    def getSetting(self, userId, var, table='settings'):
        self.cur.execute(f'SELECT {var} FROM {table} WHERE ownerId={userId} limit 1')
        setting = self.cur.fetchone()

        return setting[0] if setting else None

    #: Set the user's settings    
    def setSetting(self, userId, var, value, table='settings'):
        self.setAccount(userId)

        self.cur.execute(f'''INSERT INTO {table} (ownerId, {var}) VALUES ({userId}, '{value}') 
                        ON CONFLICT (ownerId) 
                        DO UPDATE SET {var}='{value}' WHERE EXCLUDED.ownerId={userId}''')

    #: Set magnet link in the database
    def setMagnet(self, magnetLink):
        key = uuid.uuid4().hex
        self.cur.execute(f"Insert into data (key, date, magnetLink) VALUES ('{key}', {int(time.time())}, '{magnetLink}')")

        return key