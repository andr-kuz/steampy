from steampy.client import SteamClient
from steampy._market import SteamMarketCustom


class SteamClientCustom(SteamClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.market = SteamMarketCustom(self._session)
