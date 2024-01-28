"""Connecting with Torrent Hunt API"""

from os import environ

from apis.requests import Requests


class TorrentHunt:
    def __init__(self, api_key):
        url = (
            environ.get(
                "TORRENTHUNT_API_URL",
            )
            or "https://torrenthunt.p.rapidapi.com"
        )
        self.requests = Requests()
        self.url = url.strip("/")
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Proxy-Secret": api_key,
            "X-RapidAPI-Host": "torrenthunt.p.rapidapi.com",
        }

    async def request(self, route, method="GET", params=None, data=None):
        return await self.requests.request(
            method,
            self.url + route,
            params=params,
            data=data,
            headers=self.headers,
        )
