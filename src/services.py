import json
from datetime import datetime
import config
from src.logger import setup_logger

logger = setup_logger("services", "logs/services.log")


def analyze_cashback(year: int, month: int, transactions: list[dict]) -> str:
    """Принимает список словарей транзакций и считает сумму кэшбека по категориям"""
    try:
        if not transactions:
           return "[]"
        else:
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
            logger.info("Calculated cashback by category")
            return json.dumps(cashback_, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error {e}")
        logger.error(f"Error {e}")
        return ""


if __name__ == "__main__":
    result = analyze_cashback(config.year, config.month, config.transactions)
    print(result)
