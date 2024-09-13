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

SP_500_API_KEY = os.getenv("SP_500_API_KEY")

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
    time_obj = datetime.datetime.now()
    if 6 <= time_obj.hour <= 12:
        return "Доброе утро"
    elif 13 <= time_obj.hour <= 18:
        return "Добрый день"
    elif 19 <= time_obj.hour <= 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


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




# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_currency_rates(currency: list) -> list[dict]:
	"""Получение курса валют"""
	logger.info("Beginning of the work...")
	api_key = os.getenv("API_KEY")
	for curr in currency:
		try:
			url = (
				f"https://api.apilayer.com/exchangerates_data/convert?"
				f"to=RUB&from={curr}&amount={2}"
			)
			headers = {"apikey": api_key}
			response = requests.get(url, headers=headers)
			json_result = response.json()
			amount_rub = json_result["result"]
			return amount_rub

		except Exception as e:
			logger.error(f"An error occurred while fetching the data for {curr}: {e}")

	logger.info("Formation of list of dictionaries")
	logger.info("Finish of work!")
	return result


if __name__ == "__main__":
    result = fetch_user_data("..\\data\\operations.xlsx")
    print(result)


if __name__ == "__main__":
    result_ = fetch_currency_rates(['USD', 'EUR', 'BDT'])
    print(result_)









