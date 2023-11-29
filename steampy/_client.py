from functools import partial
from steampy.client import SteamClient
from steampy._market import SteamMarketCustom
from steampy._utils import ping_proxy, REQUESRS_TIMEOUT


class SteamClientCustom(SteamClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session.request = partial(self._session.request, timeout=REQUESRS_TIMEOUT)
        self.market = SteamMarketCustom(self._session)

    def set_proxies(self, proxies: dict) -> dict:
        if not isinstance(proxies, dict):
            raise TypeError(
                'proxy must be a dict. Example: \{"http": "http://login:password@host:port"\, "https": "http://login:password@host:port"\}')
        proxy_status = ping_proxy(proxies)
        if proxy_status is True:
            self._session.proxies.update(proxies)
        return proxies
