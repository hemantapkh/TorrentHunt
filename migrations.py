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
         (id        INTEGER PRIMARY KEY AUTOINCREMENT,
         telegramId TEXT
         );''')

print('[+] Table users created successfully.')

conn.close()