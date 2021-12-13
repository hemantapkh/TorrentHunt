import json
from os import path
from models import dbQuery

import pyromod.listen
import pyrogram, py1337x
from pyrogram import Client, filters

#! Finding the absolute path of the config file
scriptPath = path.abspath(__file__)
dirPath = path.dirname(scriptPath)
configPath = path.join(dirPath,'config.json')

config = json.load(open(configPath))
language = json.load(open(config['language']))
dbSql = dbQuery(config['database'], config['magnetDatabase'])

torrent = py1337x.py1337x(proxy='1377x.to', cache=config['cache'], cacheTime=config['cacheTime'])

botId = config['botToken'].split(':')[0]
botUsername = config['botUsername']

bot = Client('my_account', config['apiId'], config['apiHash'], bot_token=config['botToken'], parse_mode='html')