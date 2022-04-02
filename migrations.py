import psycopg2

# import os, json

# config = json.load(open('src/config.json'))
# magnetDatabase = config['magnetDatabase']
# database = config['database']

choice = input('Create database for magnets? Y/[n]: ')
if choice == 'y':
    connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="magnets")

    connection.autocommit = True
    cursor = connection.cursor()

    try:
        cursor.execute('''CREATE TABLE data
                (key       TEXT PRIMARY KEY,
                date      INT,
                magnetlink TEXT
                );''')
    
        print('[+] Table users created successfully.')
    
    except psycopg2.errors.DuplicateTable:
        print('[-] Table data already exists.')

    connection.close()

choice = input('Create database for TorrentHunt? Y/[n]: ')
if choice == 'y':
    connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="torrenthunt")
    connection.autocommit = True
    
    cursor = connection.cursor()

    try:
        cursor.execute('''CREATE TABLE users
                (UserId       INTEGER PRIMARY KEY,
                date          DATE,
                userName      TEXT
                );''')

        print('[+] Table users created successfully.')
    
    except psycopg2.errors.DuplicateTable:
        print('[-] Table users already exists.')

    
    try:
        cursor.execute('''CREATE TABLE groups
                (UserId       INTEGER PRIMARY KEY,
                date          DATE,
                userName      TEXT
                );''')

        print('[+] Table users created successfully.')
    
    except psycopg2.errors.DuplicateTable:
        print('[-] Table groups already exists.')

    try:
        cursor.execute('''CREATE TABLE settings
                (ownerId       INTEGER PRIMARY KEY,
                language       TEXT DEFAULT 'english',
                defaultSite    TEXT DEFAULT 'piratebay',
                defaultMode    TEXT DEFAULT 'link',
                restrictedMode INTEGER DEFAULT 1
                );''')

        print('[+] Table settings created successfully.')
    
    except psycopg2.errors.DuplicateTable:
        print('[-] Table settings already exists.')

    try:
        cursor.execute('''CREATE TABLE flood
            (ownerId       INTEGER PRIMARY KEY,
            warned         INTEGER DEFAULT 0,
            lastMessage   INTEGER DEFAULT 0,
            blockTill     INTEGER DEFAULT 0
            );''')
            
        print('[+] Table flood created successfully.')
    
    except psycopg2.errors.DuplicateTable:
        print('[-] Table flood already exists.')

    connection.close()
