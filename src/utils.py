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
    """Приветствие пользователя"""
    utils_logger.info("Beginning of the work...")
    all_greetings = {"greeting": ("доброе утро", "добрый день", "добрый вечер", "доброй ночи")}
    current_time = datetime.datetime.now()
    if 4 <= current_time.hour <= 12:
        greet = all_greetings["greeting"][0]
    elif 12 <= current_time.hour <= 16:
        greet = all_greetings["greeting"][1]
    elif 16 <= current_time.hour <= 24:
        greet = all_greetings["greeting"][2]
    else:
        greet = all_greetings["greeting"][3]
    utils_logger.info("Finish of work")
    return greet


def analyze_dict_user_card(date: str, df) -> list[dict]:
    """Функция отображения информации о карте в заданном формате"""
    utils_logger.info("Beginning of the work...")
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
        date_begin = date_obj.replace(day=1)
        df_work = df.drop(
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
        df_work["Transaction date"] = df_work["Transaction date"].apply(
            lambda x: datetime.datetime.strptime(f"{x}", "%d.%m.%Y %H:%M:%S").date()
        )
        filtered_by_date = df_work.loc[
            (df_work["Transaction date"] <= date_obj)
            & (df_work["Transaction date"] >= date_begin)
            & (df_work["Status"] != "FAILED")
            ]
        print(filtered_by_date)
        grouped_by_card = filtered_by_date.groupby(["Card number"], as_index=False).agg({"Transaction amount": "sum"})
        result_list = []
        for index, row in grouped_by_card.iterrows():
            result_dict = {
                "Card number": row["Card number"].replace("*", ""),
                "Transaction amount": round(row["Transaction amount"], 2),
                "cashback": round(row["Transaction amount"] / 100, 2),
            }
            result_list.append(result_dict)
        utils_logger.info("Data were successfully generated. Finish of work")
        return result_list
    except ValueError:
        utils_logger.error("Error: Incorrect data")
        print("Incorrect data")


def fetch_currency_rates_values(currency_list: list[str]) -> list[dict[str, [str | int]]]:
    """Функция получения курса валют через API"""
    utils_logger.info("Beginning of the work...")

    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": f"{API_KEY}"}
    currency_rate_dict = []
    for currency in currency_list:
        payload = {"symbols": "RUB", "base": f"{currency}"}
        response = requests.get(url, headers=headers, params=payload)
        status_code = response.status_code
        if status_code == 200:
            result_j = response.json()
            currency_rate_dict.append({"currency": f"{result_j['base']}", "rate": f"{result_j['rates']['RUB']}"})
        else:
            utils_logger.info("Ошибка")
    utils_logger.info("Data were successfully generated. Finish of work")
    return currency_rate_dict


def top_user_transactions(date: str, df):
    """Функция отображения топ 5 транзакций по сумме платежа"""
    date_string_dt_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
    start_date_for_sorting = date_string_dt_obj.replace(day=1)
    dropped_df = df.drop(
        [
            "Payment date",
            "Card number",
            "Transaction currency",
            "Payment amount",
            "Payment currency",
            "Cashback",
            "MCC",
            "Bonuses (including cashback)",
            "Rounding to the investment bank",
            "The amount of the operation with rounding",
        ],
        axis=1,
    )
    dropped_df["Transaction date"] = dropped_df["Transaction date"].apply(
        lambda x: datetime.datetime.strptime(f"{x}", "%d.%m.%Y %H:%M:%S").date()
    )
    filtered_by_date = dropped_df.loc[
        (dropped_df["Transaction date"] <= date_string_dt_obj)
        & (dropped_df["Transaction date"] >= start_date_for_sorting)
        & (dropped_df["Transaction amount"].notnull())
        & (dropped_df["Status"] != "FAILED")
    ]
    sorted_df_by_transaction_amount = filtered_by_date.sort_values(
        by=["Transaction amount"], ascending=False, key=lambda x: abs(x)
    )
    top_transactions = sorted_df_by_transaction_amount[0:5]
    data_list = []
    for index, row in top_transactions.iterrows():
        data_dict = {
            "date": row["Transaction date"].strftime("%d.%m.%Y"),
            "amount": round(row["Transaction amount"], 2),
            "category": row["Category"],
            "description": row["Description"],
        }
        data_list.append(data_dict)
    utils_logger.info("Data were successfully generated. Finish of work")
    return data_list


def fetch_stock_prices_values(stocks: list) -> list[dict]:
    """Функция для получения данных об акциях из списка S&P500"""
    utils_logger.info("Beginning of the work...")
    api_key = API_KEY_SP
    stock_prices = []
    utils_logger.info("Transaction data in work")
    for stock in stocks:
        utils_logger.info("Iterating through stocks in the 'stocks' list")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        res = response.json()
        stock_prices.append({"stock": stock, "price": round(float(res["Global Quote"]["05. price"]), 2)})
    utils_logger.info("Data were successfully generated. Finish of work")
    return stock_prices



if __name__ == "__main__":
    print(df)
    print(analyze_dict_user_card("2021-11-14 14:46:24", df))
    result = fetch_currency_rates_values(["USD","EUR"])
    print(result)
    result_ = top_user_transactions("2021-11-14 14:46:24", df)
    print(result_)


