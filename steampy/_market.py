from steampy.exceptions import TooManyRequests
from steampy._exceptions import NotModified, NoListings, ErrorGettingListings, ErrorGettingHistogram
from steampy.models import SteamUrl
from steampy.market import SteamMarket
from steampy._utils import extract_games_data, extract_product_data, ProductDataTypeHint, ProductHistogramTypeHint


class SteamMarketCustom(SteamMarket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_games(self) -> dict[str, str]:
        url = SteamUrl.COMMUNITY_URL + '/market/'
        response = self._session.get(url)
        if response.status_code == 429:
            raise TooManyRequests("429 get_games()")
        return extract_games_data(response.content.decode('utf-8'))

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

    def get_product_data(self, url: str) -> ProductDataTypeHint:
        response = self._session.get(url)
        if response.status_code == 429:
            raise TooManyRequests("429 get_product_html()")
        html = response.content.decode('utf-8')
        if 'There are no listings for this item.' in html or not 'var line1=' in html:
            raise NoListings('There are no listings for this item.')
        elif 'There was an error getting listings for this item. Please try again later.' in html:
            raise ErrorGettingListings('There was an error getting listings for this item. Please try again later.')
        data = extract_product_data(html)
        return data

    def fetch_histogram(self, item_nameid: str, currency: str) -> ProductHistogramTypeHint:
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
        histogram = response.json()
        if not isinstance(histogram, dict) or not histogram.get('success') == 1:
            raise ErrorGettingHistogram('Error getting histogram')
        return response.json()
