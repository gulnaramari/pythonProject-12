from datetime import datetime
import json
from typing import Any
from src.logger import setup_logger
from src.utils import data_to_list
logger = setup_logger("services", "logs/services.log")


def analyze_cashback(year: int, month: int, list_dict: list[dict[str, Any]]) -> Any:
    """Принимает список словарей транзакций и считает сумму кэшбека по категориям"""
    try:
        cashback_: dict = {}
        for transaction in list_dict:
            transaction_date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if transaction_date.year == year and transaction_date.month == month:
                category = transaction["Категория"]
                amount = transaction["Сумма операции"]
                if amount < 0:
                    cashback_value = transaction["Кэшбэк"]
                    if cashback_value is not None and cashback_value >= 0:
                        cashback = float(cashback_value)
                    else:
                        cashback = round(amount * -0.01, 5)
                    if category in cashback_:
                        cashback_[category] += cashback
                    else:
                        cashback_[category] = cashback
        logger.info("Calculated cashback by category")
        return json.dumps(cashback_, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error {e}")
        logger.error(f"Error {e}")
        return ""


if __name__ == "__main__":
    result = analyze_cashback(2020, 2, data_to_list(r"../data/operations.xlsx"))
    print(json.dumps(result, ensure_ascii=False, indent=4))
