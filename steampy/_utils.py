from bs4 import BeautifulSoup
import json
import re
from typing import NotRequired, TypedDict

class ProductHistogramTypeHint(TypedDict):
    success: int
    sell_order_table: str
    sell_order_summary: str
    buy_order_table: str
    buy_order_summary: str
    highest_buy_order: str
    lowest_sell_order: str
    buy_order_graph: list[tuple[float, int, str]]
    sell_order_graph: list[tuple[float, int, str]]
    graph_max_y: int
    graph_min_x: float
    graph_max_x: float
    price_prefix: str
    price_suffix: str

class ProductDataTypeHint(TypedDict):
    market_hash_name: str
    item_nameid: str
    app_id: str
    sales: list[tuple[str, float, str]]
    market_ban: int
    context_id: str
    currency: str
    histogram: NotRequired[ProductHistogramTypeHint]

class ProductFullTypeHint(ProductDataTypeHint):
    histogram: ProductHistogramTypeHint

def extract_product_data(html: str) -> ProductDataTypeHint:
    context_id = '0'
    if ',"contextid":"' in html:
        context_id = (
            html
            .split(',"contextid":"')[1]
            .split('"')[0]
        )
    item_nameid = (
        html
        .split('Market_LoadOrderSpread( ')[1]
        .split(' );')[0]
    )
    name = (
        html
        .split(',"market_hash_name":"')[1]
        .split('","')[0]
    )
    market_ban = 0
    if '"market_marketable_restriction":' in html:
        market_ban = int(
            html
            .split('"market_marketable_restriction":')[1]
            .split(',')[0]
        )
    sales: list = json.loads(
        html
        .split('var line1=')[1]
        .split(']];\r\n')[0] + ']]'
    )
    app_id = (
        html
        .split('href="https://steamcommunity.com/market/search?appid=')[1]
        .split('"')[0]
    )
    currency = '1'
    if '{"wallet_currency":' in html:
        currency = (
            html
            .split('{"wallet_currency":')[1]
            .split(',')[0]
        )
    return {
        'market_hash_name': name,
        'item_nameid': item_nameid,
        'app_id': app_id,
        'sales': sales,
        'market_ban': market_ban,
        'context_id': context_id,
        'currency': currency,
    }

def extract_games_data(html: str) -> dict[str, int]:
    games = {}
    soup = BeautifulSoup(html, features='html.parser')
    game_elements = soup.select('.market_search_game_button_group a.game_button')
    for game in game_elements:
        href: str = game['href']
        appid = int(href.split('appid=')[1].split('&')[0])
        if ele := game.select_one('span.game_button_game_name'):
            name = (
                re.sub(
                    r'[\n\t\r]*', '',
                    ele.get_text()
                )
            )
            games[name] = appid
    return games

def cookie_to_string(cookie_dict: dict):
    cookie_string = "; ".join([str(x) + "=" + str(y) for x, y in cookie_dict.items()])
    return cookie_string
