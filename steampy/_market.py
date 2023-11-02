from steampy.exceptions import TooManyRequests
from steampy._exceptions import NotModified
from steampy.models import SteamUrl
from steampy.market import SteamMarket
from steampy._utils import extract_games_data, extract_product_data, cookie_to_string
from datetime import datetime


class SteamMarketCustom(SteamMarket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_games(self) -> dict[str, str]:
        url = SteamUrl.COMMUNITY_URL + '/market/'
        response = self._session.get(url)
        if response.status_code == 429:
            raise TooManyRequests("429 get_games()")
        games = extract_games_data(response.content.decode('utf-8'))
        return games

    def get_pagination(self, appid: str, start: int = 0, count: int = 100,
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

    def fetch_histogram(self, item_nameid: str, referer: str, currency: int) -> dict:
        url = SteamUrl.COMMUNITY_URL + '/market/itemordershistogram'
        cookie_dict = self._session.cookies.get_dict()
        country = cookie_dict.get('steamCountry', 'US').split('%')[0]
        time_now = datetime.utcnow()
        seconds_now = time_now.second
        seconds_rounded = seconds_now // 5 * 5
        if not seconds_rounded % 10:
            seconds_rounded += 5
        time_now_rounded = time_now.replace(second=seconds_rounded)
        time_now_rounded_str = time_now_rounded.strftime('%a, %d %b %Y %H:%M:%S GMT')
        cookie = cookie_to_string(cookie_dict)
        self._session.headers.update({
          'Accept': '*/*',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Languange': 'en-US,en;q=0.5',
          'Connection': 'keep-alive',
          'Cookie': cookie,
          'Host': 'steamcommunity.com',
          'If-Modified-Since': time_now_rounded_str,
          'Referer': referer,
          'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Mode': 'cors',
          'Sec-Fetch-Site': 'same-origin',
          'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
          'X-Requested-With': 'XMLHttpRequest',
        })
        params = {
          'country': country,
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
        if response.status_code == 200:
            return response.json()
