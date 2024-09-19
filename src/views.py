import json
import logging
import os
import pandas as pd
from dotenv import load_dotenv

from config import PATH_TO_XLSX
from src.utils import (greeting_twenty_four_hours, analyze_dict_user_card,
                       fetch_currency_rates_values, fetch_stock_prices_values,
                       top_user_transactions)

views_logger = logging.getLogger("views.log")
file_handler = logging.FileHandler("views.log", "w")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
views_logger.addHandler(file_handler)
views_logger.setLevel(logging.INFO)



load_dotenv()

API_KEY_C = os.getenv("API_KEY_C")
df = pd.read_excel(PATH_TO_XLSX)


date = input("Введите дату в формате: YYYY-MM-DD HH:MM:SS")


def main_page(date: str, df):
    """Главная страница выдает JSON ответ"""
    views_logger.info("Beginning of the work...")
    user_widget = {
        "greeting": greeting_twenty_four_hours(),
        "cards": analyze_dict_user_card(date, df),
        "top transactions": top_user_transactions(date, df),
        "currency rates": fetch_currency_rates_values(["USD","EUR"]),
        "stock_prices": fetch_stock_prices_values["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    }
    json_ = json.dumps(user_widget, indent=4, ensure_ascii=False)
    views_logger.info("Data were successfully generated. Finish of work")
    return json_


print(main_page("2020-10-15 16:40:39", df))
