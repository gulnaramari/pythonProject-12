from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

import pandas as pd

from src.logger import setup_logger
from src.utils import fetch_user_data, mod_date

logger = setup_logger("reports", "logs/reports.log")


def log(filename: Any = None) -> Callable:
    """Декоратор,который логирует вызов функции и ее результат в файл или в консоль"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                log_message = "my_function ok\n"
            except Exception as e:
                result = None
                log_message = f"my_function error: {e}. Inputs: {args}, {kwargs} \n"
            if filename:
                with open(filename, "a", encoding="utf-8") as file:
                    file.write(log_message)
            else:
                print(log_message)
            return result.to_json(path_or_buf=filename, orient='records',
                                  indent=4, force_ascii=False)

        return wrapper

    return decorator


def spending_by_category(df_transactions: pd.DataFrame, category: str, date: [str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    if date is None:
        date = datetime.now()
    else:
        date = mod_date(date)
    begin_date = date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=91)
    transactions_by_category = df_transactions.loc[
        (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) <= date)
        & (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) >= begin_date)
        & (df_transactions["Категория"] == category)
    ]
    return transactions_by_category


if __name__ == "__main__":
    result = spending_by_category(
        fetch_user_data(r"../data/operations.xlsx"), "Каршеринг", "30.12.2021 17:50:17"
    )
    print(result)
