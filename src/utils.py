import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

from src.logger import setup_logger

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_KEY_SP = os.getenv("API_KEY_SP")


logger = setup_logger("utils", "logs/utils.log")


def fetch_user_data(path: str) -> pd.DataFrame:
    """Функция принимает путь до xlsx файла и отдает датафрейм с транзакциями"""
    logger.info("Beginning of the work...")
    try:
        df_data = pd.read_excel(path)
        logger.info("Finish of the work: data are fetched")
        return df_data
    except FileNotFoundError:
        logger.info(f"File {path} not found")
        raise


def data_to_list(path) -> list[dict]:
    """Функция переводит датафрейм в список словарей"""
    logger.info("Beginning of the work...")
    try:
        df = pd.read_excel(path)
        list_dict = df.to_dict(orient="records")
        logger.info("Dataframe converted to list of dictionaries")
        return list_dict
    except FileNotFoundError:
        logger.error(f"File {path} not found")
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


def mod_date(date: str) -> datetime:
    """Функция преобразования даты"""
    logger.info(f"Received date string:{date}")
    try:
        date_obj = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
        logger.info(f"Converted to datetime object:{date_obj}")
        return date_obj
    except ValueError as e:
        logger.error(f"Error: {e}")
        raise e


def greeting_twenty_four_hours():
    """Приветствие пользователя"""
    logger.info("Beginning of the work...")
    now = datetime.now()
    current_time = now.hour
    if 6 <= current_time < 12:
        logger.info("Доброе утро")
        return "Доброе утро"
    elif 12 <= current_time < 18:
        logger.info("Добрый день")
        return "Добрый день"
    elif 18 <= current_time < 24:
        logger.info("Добрый вечер")
        return "Добрый вечер"
    else:
        logger.info("Доброй ночи")
        return "Доброй ночи"


def analyze_dict_user_card(df_data: pd.DataFrame) -> list[dict]:
    """Функция создает словарь с расходами по каждой карте"""
    logger.info("Beginning of the work...")
    filtered_card = df_data[df_data["Номер карты"] != ""]
    print(filtered_card.head(10))
    cards_groupping = (
        filtered_card.loc[df_data["Сумма платежа"] < 0].groupby("Номер карты")["Сумма платежа"].sum().to_dict()
    )
    logger.debug(f"Cards have been grouped: {cards_groupping}")

    card_expense = []
    for card, expense in cards_groupping.items():
        card_expense.append(
            {"last_digits": card, "total_spent": abs(expense), "cashback": abs(round(expense / 100, 2))}
        )
        logger.info(f"Expenses on card {card} were added: {abs(expense)}")

    logger.info("Finish of the work: data on card's expenses were analyzed")
    return card_expense


def top_user_transactions(df_data) -> list[dict]:
    """Функция принимает список транзакций и выводит топ 5 операций по сумме платежа"""
    logger.info("Beginning of the work...")

    filtered_data = df_data[(df_data["Категория"] != "Переводы") & (df_data["Категория"] != "Пополнения")]
    print(filtered_data.head(10))

    top_transactions = filtered_data.sort_values(by="Сумма операции", ascending=True).iloc[:5]
    print(top_transactions)
    result_ = top_transactions.to_dict(orient="records")

    top_list = []
    for transaction in result_:
        top_list.append(
            {
                "Дата операции": transaction["Дата операции"],
                "Сумма операции": transaction["Сумма операции"],
                "Категория": transaction["Категория"],
                "Описание": transaction["Описание"],
            }
        )
    logger.info("Five top transactions were received")
    return top_list


def fetch_currency_rates_values(currency_list: list[str]) -> list[dict[str, [str | int]]]:
    """Функция получения курса валют через API"""
    logger.info("Beginning of the work...")
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
            logger.info("Error")
    logger.info("Data were successfully generated. Finish of work")
    return currency_rate_dict


def fetch_stock_prices_values(stocks: list) -> list[dict]:
    """Функция для получения данных об акциях из списка S&P500"""
    logger.info("Beginning of the work...")
    api_key = API_KEY_SP
    stock_prices = []
    logger.info("Transaction data in work")
    for stock in stocks:
        logger.info("Iterating through stocks in the 'stocks' list")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        res = response.json()
        stock_prices.append({"stock": stock, "price": round(float(res["Global Quote"]["05. price"]), 2)})
    logger.info("Data were successfully generated. Finish of work")
    return stock_prices


def transaction_filter(df_data: pd.DataFrame, date: str) -> pd.DataFrame:
    """Функция, по сути, фильтрация датафрейма по заданной дате"""
    logger.info("Beginning of the work...")
    date_ = mod_date(date)
    logger.debug(f"End date: {date_}")
    begin_date = date_.replace(day=1)
    logger.debug(f"Begin date: {begin_date}")
    date_end = date_.replace(hour=0, minute=0, second=0) + timedelta(days=1)
    logger.debug(f"End date: {date_end}")
    transaction_ = df_data.loc[
        (pd.to_datetime(df_data["Дата операции"], dayfirst=True) <= date_end)
        & (pd.to_datetime(df_data["Дата операции"], dayfirst=True) >= begin_date)
    ]
    logger.info(f"DataFrame was received {transaction_}")

    return transaction_


if __name__ == "__main__":
    result = fetch_user_data(r"../data/operations.xlsx")
    print(result)

if __name__ == "__main__":
    result_expenses_cards = analyze_dict_user_card(fetch_user_data(r"../data/operations.xlsx"))
    print(result_expenses_cards)

if __name__ == "__main__":
    top_ = top_user_transactions(fetch_user_data(r"../data/operations.xlsx"))
    print(top_)

if __name__ == "__main__":
    transaction_res = transaction_filter(fetch_user_data(r"../data/operations.xlsx"), "21.03.2019 17:01:38")
    print(transaction_res)
