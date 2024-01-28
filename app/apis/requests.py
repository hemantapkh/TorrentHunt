"""Async requests using aioHttp"""

import aiohttp
from loguru import logger


class Requests:
    # Perform async HTTP request
    async def request(self, method, url, params=None, data=None, headers=None):
        self.connector = aiohttp.TCPConnector(verify_ssl=False)
        self.session = aiohttp.ClientSession(connector=self.connector)

        try:
            async with aiohttp.ClientSession(connector=self.connector) as session:
                async with session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    headers=headers,
                ) as resp:
                    try:
                        return await resp.json()

                    except aiohttp.client_exceptions.ContentTypeError:
                        return await resp.text()

        except Exception as err:
            logger.error(
                "HTTP Error: {} {} PARAMS: {} DATA: {} HEADERS: {} ERR: {}".format(
                    method,
                    url,
                    params,
                    data,
                    headers,
                    err,
                ),
            )
            return {
                "success": False,
                "error": f"APIexception: {err}",
            }

    # Perform async GET request
    async def get(self, url, params=None, headers=None):
        return await self.request("GET", url, params=params, headers=headers)

    # Perform async POST request
    async def post(self, url, data=None, headers=None):
        return await self.request("POST", url, data=data, headers=headers)
