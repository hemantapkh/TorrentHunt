'''Connecting with Torrent Hunt API'''

from .requests import Requests


class TorrentHunt():
    def __init__(self, url, api_key):
        self.requests = Requests()
        self.url = url.strip('/')
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Proxy-Secret': api_key,
            'X-RapidAPI-Host': 'torrenthunt.p.rapidapi.com',
        }

    async def request(self, route, method='GET', params=None, data=None):
        return await self.requests.request(
            method, self.url+route, params=params, data=data, headers=self.headers,
        )
