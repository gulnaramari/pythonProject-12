import datetime
import logging
import os
import pandas as pd
from dotenv import load_dotenv
import json
import requests
import urllib.request


load_dotenv(".env")

# Проверка загрузки API_KEY
api_key = os.getenv("API_KEY")
print(" ")

# Проверка загрузки API_KEY_C
API_KEY_C = os.getenv("API_KEY_C")
print("")

API_KEY_SP = os.getenv("API_KEY_SP")
print(" ")

logger = logging.getLogger("utils.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(filename)s: %(levelname)s: %(message)s",
    filename="../logs/utils.log",
    filemode="w",
)


def fetch_user_data(path_file: str) -> list[dict]:
    """ Читает xlsx файл и возвращает список словарей"""
    df = pd.read_excel(path_file)

    result = df.apply(
        lambda row: {
            "Дата платежа": row["Дата платежа"],
            "Статус": row["Статус"],
            "Сумма платежа": row["Сумма платежа"],
            "Валюта платежа": row["Валюта платежа"],
            "Категория": row["Категория"],
            "Описание": row["Описание"],
            "Номер карты": row["Номер карты"],
        },
        axis=1,
    ).tolist()
    return result


def greeting_twenty_four_hours():
    """Приветствие"""
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
    logger.info("Beginning of the work...")
    cards = {}
    result = []

    try:
        for i in all_data:
            if i["Номер карты"] == "nan" or type(i["Номер карты"]) is float:
                continue
            elif i["Сумма платежа"] == "nan":
                continue
            else:
                if i["Номер карты"][1:] in cards:
                    cards[i["Номер карты"][1:]] += float(str(i["Сумма платежа"])[1:])
                else:
                    cards[i["Номер карты"][1:]] = float(str(i["Сумма платежа"])[1:])
        for key, value in cards.items():
            result.append({"last_digits": key, "total_spent": round(value, 2), "cashback": round(value/ 100, 2)})
    except FileNotFoundError:
        logger.warning("File not found. Incorrect path to file")
        print("Файл не найден")
        return []
    logger.info("The work is completed")
    return result


def fetch_currency_rates_values(currency: list) -> list[dict]:
    """Функция запроса курса валют"""
    logger.info("Начало работы функции (currency_rates)")
    api_key = API_KEY_C
    result = []
    for i in currency:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{i}"
        with urllib.request.urlopen(url) as response:
            body_json = response.read()
        body_dict = json.loads(body_json)
        result.append({"currency": i, "rate": round(body_dict["conversion_rates"]["RUB"], 2)})

    logger.info("Создание списка словарей для функции - currency_rates")

    logger.info("Окончание работы функции - currency_rates")
    return result


def top_user_transactions(my_list: list) -> list:
    """Функция для получения топ-5 транзакций по сумме платежа"""
    logger.info("Начало работы функции (top_five_transaction)")
    all_transactions = {}
    result = []
    logger.info("Перебор транзакций в функции (top_five_transaction)")
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
    logger.info("Окончание работы функции (top_five_transaction)")

    return result


def fetch_stock_prices_values(stocks: list) -> list:
    """Функция для получения данных об акциях из списка S&P500"""
    logger.info("Начало работы функции (get_price_stock)")
    api_key = API_KEY_SP
    stock_prices = []
    logger.info("Функция обрабатывает данные транзакций.")
    for stock in stocks:
        logger.info("Перебор акций в списке 'stocks' в функции (get_price_stock)")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        result = response.json()

        stock_prices.append({"stock": stock, "price": round(float(result["Global Quote"]["05. price"]), 2)})
    logger.info("Функция get_price_stock успешно завершила свою работу")
    return stock_prices




if __name__ == "__main__":
    result = fetch_user_data("..\\data\\operations.xlsx")
    print(result)

