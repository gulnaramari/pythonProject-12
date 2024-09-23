import json
from datetime import datetime
import config
import logging

services_logger = logging.getLogger("views")
file_handler = logging.FileHandler("../logs/views.log", "w")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.INFO)


def analyze_cashback(year: int, month: int, transactions: list[dict]) -> str:
    """Принимает список словарей транзакций и считает сумму кэшбека по категориям"""
    try:
        cashback_: dict = {}
        for transaction in transactions:
            transaction_date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if transaction_date.year == year and transaction_date.month == month:
                category = transaction["Категория"]
                amount = transaction["Сумма операции"]
                if amount < 0:
                    cashback_value = transaction["Кэшбэк"]
                    if cashback_value is not None and cashback_value >= 0:
                        cashback = round(float(cashback_value), 5)
                    else:
                        cashback = round(amount * -0.01, 5)
                    if category in cashback_:
                        cashback_[category] += cashback
                    else:
                        cashback_[category] = cashback
        services_logger.info("Calculated cashback by category")
        return json.dumps(cashback_, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error {e}")
        services_logger.error(f"Error {e}")
        return ""


if __name__ == "__main__":
    result = analyze_cashback(config.year, config.month, config.transactions)
    print(result)
