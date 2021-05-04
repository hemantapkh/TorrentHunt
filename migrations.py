import sqlite3
import os, json

config = json.load(open('config.json'))
database = config['database']

if os.path.exists(database):
    os.remove(database)
    print('[-] Database already exists. Deleting it.')

conn = sqlite3.connect(database)
print('[+] Database opened successfully.')

conn.execute('''CREATE TABLE users
         (UserId       INTEGER PRIMARY KEY
         );''')

print('[+] Table users created successfully.')

conn.execute('''CREATE TABLE settings
         (ownerId       INTEGER PRIMARY KEY,
         language       TEXT DEFAULT "EN"
         );''')

print('[+] Table settings created successfully.')

conn.close()