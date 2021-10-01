import requests
from src.objs import *
from ast import literal_eval
from src.functions.keyboard import notSubscribedMarkup

#: URL shortner
def shortner(url):
    short = requests.get(f'http://tinyurl.com/api-create.php?url={url}')
    return short.text

#: Get suggestion query
def getSuggestions(query):
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0'}

    params = (
        ('client', 'Firefox'),
        ('q', query),
    )

    response = requests.get('https://www.google.com/complete/search', headers=headers, params=params)
    
    return literal_eval(response.text)[1]

#: Sort list according to the length of elements
def sortList(lst):
    lst2 = sorted(lst, key=len)
    return lst2

# Check if the user is subscribed or not, returns True if subscribed
def isSubscribed(message, userLanguage=None, sendMessage=True):
    telegramId = message.from_user.id
    subscribed = True
    
    try:
        status = bot.get_chat_member('-1001270853324', telegramId)
        if status.status == 'left':
            subscribed = False
        else:
            return True

    except Exception:
        subscribed = True

    if not subscribed:
        # Send the links if sendMessage is True
        if sendMessage:
            bot.send_message(message.chat.id, text=language['notSubscribed'][userLanguage], reply_markup=notSubscribedMarkup(userLanguage))
        return False

# Returns the equivalent category of the text 
def textToCategory(text, userLanguage):
    if text == language['moviesBtn'][userLanguage]:
        return 'movies'
    
    elif text == language['tvBtn'][userLanguage]:
        return 'tv'

    elif text == language['docsBtn'][userLanguage]:
        return 'documentaries'

    elif text == language['gamesBtn'][userLanguage]:
        return 'games'

    elif text == language['musicBtn'][userLanguage]:
        return 'music'

    elif text == language['appsBtn'][userLanguage]:
        return 'apps'

    elif text == language['animeBtn'][userLanguage]:
        return 'anime'

    elif text == language['xxxBtn'][userLanguage]:
        return 'xxx'

    elif text == language['othersBtn'][userLanguage]:
        return 'other'

    elif text == language['allBtn'][userLanguage]:
        return 'all'

    else:
        return None