import json
from typing import Any
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from src.utils import (
    analyze_dict_user_card,
    fetch_currency_rates_values,
    fetch_stock_prices_values,
    fetch_user_data, data_to_list,
    greeting_twenty_four_hours,
    top_user_transactions,
    setup_logger
)

with open("../data/user_settings.json", "r") as file:
    user_choice = json.load(file)

load_dotenv()

logger = setup_logger("views", "views.log")


def main_json(input_date: str, user_settings: Any) -> Any:
    """Основная функция для генерации JSON-ответа."""
    path = r"../data/operations.xlsx"
    df_data = fetch_user_data(path)

    end_date = datetime.strptime(input_date, '%Y.%m.%d %H:%M:%S')
    start_date = end_date.replace(day=1, hour=0, second=0, minute=0)

    filtered_data = df_data[(pd.to_datetime(df_data['Дата операции']) >= start_date) &
                            (pd.to_datetime(df_data['Дата операции']) <= end_date) &
                            (df_data['Сумма операции'] < 0)]

    cards_data = analyze_dict_user_card(filtered_data)
    currency_rates = fetch_currency_rates_values(user_settings["user_currencies"])
    # stocks_cost = fetch_stock_prices_values(user_settings["user_stocks"])
    top_transactions = top_user_transactions(filtered_data)
    greetings = greeting_twenty_four_hours()
    user_data = {
        "greeting": greetings,
        "cards": cards_data,
        "top_transactions": top_transactions,
        "exchange_rates": currency_rates,
        # "stocks": stocks_cost,
    }
    return json.dumps(user_data, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    result = main_json("14.03.2020", user_choice)
    print(result)
