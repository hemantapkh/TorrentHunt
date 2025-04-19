"""Connecting with Torrent Hunt API"""

from os import environ

from apis.requests import Requests


class TorrentHunt:
    def __init__(self, api_key):
        url = (
            environ.get(
                "TORRENTHUNT_API_URL"
            )
        )
        self.requests = Requests()
        self.url = url.strip("/")
        self.headers = {
            "X-API-Key": environ.get("TORRENTHUNT_API_KEY"),
        }

    async def request(self, route, method="GET", params=None, data=None):
        return await self.requests.request(
            method,
            self.url + route,
            params=params,
            data=data,
            headers=self.headers
        )
