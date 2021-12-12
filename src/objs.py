import json
from os import path
from models import dbQuery

import telebot, py1337x

#! Finding the absolute path of the config file
scriptPath = path.abspath(__file__)
dirPath = path.dirname(scriptPath)
configPath = path.join(dirPath,'config.json')

config = json.load(open(configPath))
language = json.load(open(config['language']))
dbSql = dbQuery(config['database'], config['magnetDatabase'])

torrent = py1337x.py1337x(proxy='1337xx.to', cache=config['cache'], cacheTime=config['cacheTime'])

botId = config['botToken'].split(':')[0]
bot = telebot.TeleBot(config['botToken'], parse_mode='HTML')
botUsername = '@'+bot.get_me().username