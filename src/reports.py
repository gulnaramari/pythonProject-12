import datetime as dt
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

import pandas as pd

from src.logger import setup_logger
from src.utils import fetch_user_data, mod_date

logger = setup_logger("reports", "logs/reports.log")


def report_to_log(filename: Any = None) -> Callable:
    """Декоратор логирует вызов функции """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                message = f"{func.__name__} ok"

                if not filename:
                    print(message)
                else:
                    with open(filename, "a") as file:
                        file.write(message)

                result_ = result.to_json(
                    path_or_buf=filename,
                    orient='records',
                    indent=4, force_ascii=False
                )
                return result_  # пускаем датафрейм от функции дальше, "на выход" из декоратора, не меняя его.
            except Exception as e:
                error_message = (
                    f"{func.__name__}:"
                    f" {e.__class__.__name__}."
                    f" Inputs: {args}, {kwargs}"
                )
                if not filename:
                    print(error_message)
                else:
                    with open(filename, "a") as file:
                        file.write(error_message)
                raise

        return wrapper

    return decorator


@report_to_log('output.json')
def spending_by_category(df_transactions: pd.DataFrame, category: str, date: [str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    logger.info("Beginning of the work...")
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
    logger.info("Finish of the work: data were analyzed")
    return transactions_by_category


if __name__ == "__main__":
    result = spending_by_category(
        fetch_user_data(r"../data/operations.xlsx"), "Супермаркеты", "28.12.2020 17:50:17"
    )
    print(result)
