import json
from typing import Any

from dotenv import load_dotenv

from src.logger import setup_logger
from src.utils import (analyze_dict_user_card, fetch_currency_rates_values, fetch_stock_prices_values, fetch_user_data,
                       greeting_twenty_four_hours, top_user_transactions)

with open("../data/user_settings.json", "r") as file:
    user_choice = json.load(file)

load_dotenv()

logger = setup_logger("views", "logs/views.log")


def main_json(input_date: str, user_settings: Any) -> Any:
    """Основная функция для генерации JSON-ответа."""
    path = r"../data/operations.xlsx"
    df_data = fetch_user_data(path)
    cards_data = analyze_dict_user_card(df_data)
    currency_rates = fetch_currency_rates_values(user_settings["user_currencies"])
    stocks_cost = fetch_stock_prices_values(user_settings["user_stocks"])
    top_transactions = top_user_transactions(df_data)
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
