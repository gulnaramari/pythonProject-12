import json
import logging

from src.utils import (fetch_user_data, fetch_currency_rates_values, fetch_stock_prices_values,
                       analyze_dict_user_card, greeting_twenty_four_hours, top_user_transactions)
from src.views import filter_by_date

logger = logging.getLogger("utils.log")
file_handler = logging.FileHandler("main.log", "w")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

data_frame = fetch_user_data("../data/operations.xlsx")


def main(date: str, df_transactions, stocks: list, currency: list):
    """Функция создающая JSON ответ для страницы Главная"""
    logger.info("Начало работы главной функции (main)")
    final_list = filter_by_date(date, df_transactions)
    greeting = greeting_twenty_four_hours()
    cards = analyze_dict_user_card(final_list)
    top_trans = top_user_transactions(final_list)
    stocks_prices = fetch_stock_prices_values(stocks)
    currency_r = fetch_currency_rates_values(currency)
    logger.info("Создание JSON ответа")
    result = [{
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_trans,
            "currency_rates": currency_r,
            "stock_prices": stocks_prices,
        }]
    date_json = json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
    )
    logger.info("Завершение работы ")
    return date_json
