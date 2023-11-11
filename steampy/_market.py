from steampy.exceptions import TooManyRequests
from steampy._exceptions import NotModified
from steampy.models import SteamUrl
from steampy.market import SteamMarket
from steampy._utils import extract_games_data, extract_product_data


class SteamMarketCustom(SteamMarket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_games(self) -> dict[str, int]:
        url = SteamUrl.COMMUNITY_URL + '/market/'
        response = self._session.get(url)
        if response.status_code == 429:
            raise TooManyRequests("429 get_games()")
        games = extract_games_data(response.content.decode('utf-8'))
        return games

    def get_page(self, appid: str, start: int = 0, count: int = 100,
                       sort_column: str = '', sort_dir: str = '') -> dict:
        url = SteamUrl.COMMUNITY_URL + '/market/search/render/'
        params = {
          'appid': appid,
          'start': start,
          'count': count,
          'norender': 1,
          'sort_column': sort_column,
          'sort_dir': sort_dir
        }
        response = self._session.get(url, params=params)
        if response.status_code == 429:
            raise TooManyRequests("429 get_pagination()")
        data = response.json()
        return data

    def get_product_data(self, url: str) -> dict:
        response = self._session.get(url)
        if response.status_code == 429:
            raise TooManyRequests("429 get_product_html()")
        data = extract_product_data(response.content.decode('utf-8'))
        return data

    def fetch_histogram(self, item_nameid: str, currency: int) -> dict:
        url = SteamUrl.COMMUNITY_URL + '/market/itemordershistogram'
        params = {
          'country': 'US',
          'language': 'english',
          'currency': currency,
          'item_nameid': item_nameid,
          'two_factor': 0
        }
        response = self._session.get(url, params=params)
        if response.status_code == 429:
            raise TooManyRequests("429 fetch_histogram()")
        if response.status_code == 304:
            raise NotModified("304 fetch_histogram(). Try again in 5 seconds")
        return response.json()
