import datetime
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
import requests
from src.logger import setup_logger

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_KEY_SP = os.getenv("API_KEY_SP")


logger = setup_logger("utils", "logs/utils.log")


def fetch_user_data(path: str) -> list[dict]:
    """Функция принимает путь до xlsx файла и создает список словарей с транзакциями"""
    try:
        df = pd.read_excel(path)
        logger.info("Beginning of the work...")
        logger.info("Finish of the work")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error {e}")
        logger.error(f"Error {e}")
        return []


def filter_transactions_by_date(transactions: list[dict], date: str) -> list[dict]:
    """Функция фильтрует транзакции с начала месяца, на который выпадает входящая дата по входящую дату"""
    date_ = datetime.strptime(date, "%d.%m.%Y")
    end_date = date_ + timedelta(days=1)
    begin_date = datetime(end_date.year, end_date.month, 1)

    def parse_date(date_str: str) -> datetime:
        """Функция переводит дату из формата строки в формат datetime"""
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

    filtered_transactions = [
        transaction
        for transaction in transactions
        if begin_date <= parse_date(transaction["Дата операции"]) <= end_date
    ]
    logger.info(f"Filtrated by date from {begin_date} to {end_date}")
    return filtered_transactions


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


def analyze_dict_user_card(transactions: list[dict]) -> list[dict]:
    """Функция создает словарь с суммой общих трат и суммой кэшбека"""
    try:
        cards_data = {}
        for transaction in transactions:
            card_number = transaction.get("Номер карты")
            if not card_number:
                continue
            amount = float(transaction["Сумма операции"])
            if card_number not in cards_data:
                cards_data[card_number] = {"total_spent": 0.0, "cashback": 0.0}
            if amount < 0:
                cards_data[card_number]["total_spent"] += abs(amount)
                cashback_value = transaction.get("Кэшбэк")
                if transaction["Категория"] != "Переводы" and transaction["Категория"] != "Пополнения":
                    # рассчитываем кэшбек как 1% от траты, но если поле кешбек содержит сумму просто ее добавляем
                    if cashback_value is not None:
                        cashback_amount = float(cashback_value)
                        if cashback_amount >= 0:
                            cards_data[card_number]["cashback"] += cashback_amount
                        else:
                            cards_data[card_number]["cashback"] += amount * -0.01
                    else:
                        cards_data[card_number]["cashback"] += amount * -0.01
        logger.info("Cashback and card amounts have been calculated")
        each_card = []
        for last_digits, data in cards_data.items():
            each_card.append(
                {
                    "last_digits": last_digits,
                    "total_spent": round(data["total_spent"], 2),
                    "cashback": round(data["cashback"], 2),
                }
            )
        logger.info("Cashback and amounts calculated for each card")
        return each_card
    except ValueError:
        logger.error("Error: Incorrect data")
        print("Incorrect data")


def top_user_transactions(transactions: list[dict]) -> list[dict]:
    """Функция принимает список транзакций и выводит топ 5 операций по сумме платежа"""
    sorted_transactions = sorted(transactions, key=lambda x: float(x["Сумма операции"]), reverse=True)
    top_transactions = []
    for transaction in sorted_transactions[:5]:
        date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S").strftime("%d.%m.%Y")
        top_transactions.append(
            {
                "Дата операции": date,
                "Сумма операции": transaction["Сумма операции"],
                "Категория": transaction["Категория"],
                "Описание": transaction["Описание"],
            }
        )
    logger.info("Five top transactions received")
    return top_transactions


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
