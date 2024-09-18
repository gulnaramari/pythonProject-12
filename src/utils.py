import datetime
import json
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from config import PATH_TO_XLSX

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_KEY_SP = os.getenv("API_KEY_SP")

df = pd.read_excel(PATH_TO_XLSX)
df.columns = [
    "Transaction date",
    "Payment date",
    "Card number",
    "Status",
    "Transaction amount",
    "Transaction currency",
    "Payment amount",
    "Payment currency",
    "Cashback",
    "Category",
    "MCC",
    "Description",
    "Bonuses (including cashback)",
    "Rounding to the investment bank",
    "The amount of the operation with rounding",
]

# Настройки логера
utils_logger = logging.getLogger("utils")
file_handler = logging.FileHandler("utils.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.INFO)


def greeting_twenty_four_hours():
    """Приветствие"""
    utils_logger.info("Beginning of the work...")
    dict_all = {"greeting": ("доброе утро", "добрый день", "добрый вечер", "доброй ночи")}
    current_time = datetime.datetime.now()
    if current_time.hour >= 4 and current_time.hour <= 12:
        greet = dict_all["greeting"][0]
    elif current_time.hour >= 12 and current_time.hour <= 16:
        greet = dict_all["greeting"][1]
    elif current_time.hour >= 16 and current_time.hour <= 24:
        greet = dict_all["greeting"][2]
    else:
        greet = dict_all["greeting"][3]
    return greet


def analyze_dict_user_card(all_data: list) -> list:
    """Создает словарь по каждой карте"""
    utils_logger.info("Beginning of the work...")
    try:
        date_string_dt_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").date()
        start_date_for_sorting = date_string_dt_obj.replace(day=1)
        edited_df = DataFrame.drop(
            [
                "Payment date",
                "Transaction currency",
                "Payment amount",
                "Payment currency",
                "Cashback",
                "Category",
                "MCC",
                "Description",
                "Bonuses (including cashback)",
                "Rounding to the investment bank",
                "The amount of the operation with rounding",
            ],
            axis=1,
        )
        edited_df["Transaction date"] = edited_df["Transaction date"].apply(
            lambda x: datetime.datetime.strptime(f"{x}", "%d.%m.%Y %H:%M:%S").date()
        )
        filtered_df_by_date = edited_df.loc[
            (edited_df["Transaction date"] <= date_string_dt_obj)
            & (edited_df["Transaction date"] >= start_date_for_sorting)
            & (edited_df["Card number"].notnull())
            & (edited_df["Transaction amount"] <= 0)
            & (edited_df["Status"] != "FAILED")
            ]
        grouped_df = filtered_df_by_date.groupby(["Card number"], as_index=False).agg({"Transaction amount": "sum"})
        data_list = []
        for index, row in grouped_df.iterrows():
            data_dict = {
                "Card number": row["Card number"].replace("*", ""),
                "Transaction amount": round(row["Transaction amount"], 2),
                "cashback": round(row["Transaction amount"] / 100, 2),
            }
            data_list.append(data_dict)
        utils_logger.info("Данные по картам успешно сформированны")
        return data_list
    except ValueError:
        print("Неверный формат даты")
        utils_logger.error("Ошибка ввода данных: неверный формат даты")

def fetch_currency_rates_values(currency_list: list[str]) -> dict[str, [str | int]]:
    """Функция получения курса валют через API"""
    utils_logger.info("Beginning of the work...")

    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": f"{API_KEY}"}
    currency_rate_dict = {}
    for currency in currency_list:
        payload = {"symbols": "RUB", "base": f"{currency}"}
        response = requests.get(url, headers=headers, params=payload)
        status_code = response.status_code
        if status_code == 200:
            result = response.json()
            currency_rate_dict = {"currency": f"{result['base']}", "rate": f"{result['rates']['RUB']}"}
        else:
            print(f"Запрос не был успешным.")
            utils_logger.info("Запрос не удался")
    utils_logger.info("Данные по курсу валют успешно получены")
    return currency_rate_dict


def top_user_transactions(my_list: list) -> list:
    """Функция для получения топ-5 транзакций по сумме платежа"""
    utils_logger.info("Beginning of the work...")
    all_transactions = {}
    result = []
    utils_logger.info("Перебор транзакций в функции (top_five_transaction)")
    for i in my_list:
        if i["Категория"] not in all_transactions and str(i["Сумма платежа"])[0:1] != "-":
            if i["Категория"] != "Пополнения":
                all_transactions[i["Категория"]] = float(str(i["Сумма платежа"])[1:])
        elif (
                i["Категория"] in all_transactions
                and float(str(i["Сумма платежа"])[1:]) > all_transactions[i["Категория"]]
        ):
            all_transactions[i["Категория"]] = float(str(i["Сумма платежа"])[1:])
    for i in my_list:
        for k, v in all_transactions.items():
            if k == i["Категория"] and v == float(str(i["Сумма платежа"])[1:]):
                result.append({"date": i["Дата платежа"], "amount": v, "category": k, "description": i["Описание"]})
    utils_logger.info("Окончание работы функции (top_five_transaction)")

    return result


def fetch_stock_prices_values(stocks: list) -> list[dict]:
    """Функция для получения данных об акциях из списка S&P500"""
    utils_logger.info("Beginning of the work...")
    api_key = API_KEY_SP
    stock_prices = []
    utils_logger.info("Функция обрабатывает данные транзакций.")
    for stock in stocks:
        utils_logger.info("Перебор акций в списке 'stocks' в функции (get_price_stock)")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        result = response.json()
        stock_prices.append({"stock": stock, "price": round(float(result["Global Quote"]["05. price"]), 2)})
    utils_logger.info("")
    return stock_prices


if __name__ == "__main__":
    print(df)
    result = fetch_currency_rates_values(["USD"])
    print(result)
    result_sp = fetch_stock_prices_values(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    print(result_sp)
