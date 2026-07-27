"""HTTP transport mixin for providers backed by HTTP APIs.

Standalone — it knows nothing about the search interface. HTTP-backed
providers combine it with the interface, transport first so its concrete
`close` wins the method resolution order:

    class MyProvider(HttpProvider, TorrentProvider): ...

Subclasses use `self.session` (a lazily created aiohttp session) directly.
"""

import aiohttp


class HttpProvider:
    def __init__(self, base_url: str, timeout: float = 40):
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=float(timeout))
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
