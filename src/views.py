import json
import logging
from dotenv import load_dotenv
from typing import Any
from src.utils import (fetch_user_data, filter_transactions_by_date,
                       greeting_twenty_four_hours, analyze_dict_user_card,
                       fetch_currency_rates_values, fetch_stock_prices_values,
                       top_user_transactions)

with open("../data/user_settings.json", "r") as file:
    user_choice = json.load(file)
input_date_str = "14.03.2020"
load_dotenv()


views_logger = logging.getLogger("views")
file_handler = logging.FileHandler("../logs/views.log", "w")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
views_logger.addHandler(file_handler)
views_logger.setLevel(logging.INFO)


def main_json(input_date: Any, user_settings: Any) -> Any:
    """Основная функция для генерации JSON-ответа."""
    path = r"../data/operations.xlsx"
    transactions = fetch_user_data(path)
    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    cards_data = analyze_dict_user_card(filtered_transactions)
    currency_rates = fetch_currency_rates_values(user_settings["user_currencies"])
    stocks_cost = fetch_stock_prices_values(user_settings["user_stocks"])
    top_transactions = top_user_transactions(filtered_transactions)
    greetings = greeting_twenty_four_hours()
    user_data = {
        "greeting": greetings,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "exchange_rates": currency_rates,
        "stocks": stocks_cost,
    }
    return json.dumps(user_data, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    result = main_json("14.03.2020", user_choice)
    print(result)

