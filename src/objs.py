import json
from os import path
from models import dbQuery

import telebot, py1337x
from tpblite import TPB

#! Finding the absolute path of the config file
scriptPath = path.abspath(__file__)
dirPath = path.dirname(scriptPath)
configPath = path.join(dirPath,'config.json')

config = json.load(open(configPath))
language = json.load(open(config['language']))
dbSql = dbQuery(config['database'])

torrent = py1337x.py1337x(proxy='1337x.to', cache=config['cache'], cacheTime=config['cacheTime'])
pirateBay = TPB()

bot = telebot.TeleBot(config['botToken'], parse_mode='HTML')