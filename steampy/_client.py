import requests
from steampy import guard
from steampy.client import SteamClient
from steampy._market import SteamMarketCustom


class SteamClientCustom(SteamClient):
    def __init__(self, api_key: str, username: str = None, password: str = None, steam_guard: str = None,
                 login_cookies: dict = None, proxies: dict = None):
        self._api_key = api_key
        self._session = requests.Session()
        if proxies:
            self.set_proxies(proxies)
        self.steam_guard_string = steam_guard
        if self.steam_guard_string is not None:
            self.steam_guard = guard.load_steam_guard(self.steam_guard_string)
        else:
            self.steam_guard = None
        self.was_login_executed = False
        self.username = username
        self._password = password
        self.market = SteamMarketCustom(self._session)
        if login_cookies:
            self.set_login_cookies(login_cookies)
