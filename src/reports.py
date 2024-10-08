import datetime as dt
import functools
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

import config
from src.logger import setup_logger
from src.utils import fetch_user_data, mod_date

logger = setup_logger("reports", "logs/reports.log")


def report_to_file_default(func: Callable) -> Callable:
    """Записывает в файл результат, который возвращает функция, формирующая отчет."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        with open("function_operation_report.txt", "w") as file:
            file.write(str(result))
        logger.info(f"Записан результат работы функции {func}")
        return result

    return wrapper


# дата гггг.мм.дд
@report_to_file_default
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца
    от переданной даты"""
    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        if date is None:
            fin_date = datetime.now()
        else:
            fin_date = mod_date(date)
        start_date = fin_date.replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=91)
        filtered_transactions = transactions[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= date)
            & (transactions["Категория"] == category)
        ]
        grouped_transactions = filtered_transactions.groupby(pd.Grouper(key="Дата операции", freq="ME")).sum()
        logger.info(f"Траты за последние три месяца от {date} по категории {category}")
        return grouped_transactions.to_dict(orient="records")
    except Exception as e:
        print(f"Возникла ошибка {e}")
        logger.error(f"Возникла ошибка {e}")



if __name__ == "__main__":
    result = spending_by_category(
        config.transactions, "Супермаркеты", "31.12.2021 15:44:39"
    )
    print(result)
