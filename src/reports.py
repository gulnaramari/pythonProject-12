import functools
from datetime import datetime, timedelta
import logging
from typing import Any, Callable
import pandas as pd
import config


reports_logger = logging.getLogger("reports")
file_handler = logging.FileHandler("../logs/utils.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
reports_logger.addHandler(file_handler)
reports_logger.setLevel(logging.INFO)

def report_to_file_now(func: Callable) -> Callable:
    """Записывает в файл результат, который возвращает функция, формирующая отчет."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        with open("function_operation_report.txt", "a") as file:  # Changed to append mode
            file.write(str(result) + "\n")  # Added newline for better readability
        reports_logger.info(f"The result of the function {func.__name__} is recorded.")
        return result

    return wrapper


def report_to_file(filename: str = "function_operation_report.txt") -> Callable:
    """Записывает в переданный файл результат, который возвращает функция, формирующая отчет."""
    def decorator(func: Callable[[tuple[Any, ...], dict[str, Any]], Any]) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            with open(filename, "a") as file:
                file.write(str(result) + "\n")
            reports_logger.info(f"The result of the function {func.__name__} is recorded to {filename}.")
            return result
        return wrapper
    return decorator


@report_to_file_now
def spending_by_category(transactions: pd.DataFrame, category: str, date: Any = None) -> Any:

    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        if date is None:
            date = datetime.now()
        else:
            date = pd.to_datetime(date, format="%Y.%m.%d")

        start_date = date - timedelta(days=date.day - 1) - timedelta(days=90)
        filtered_transactions = transactions[
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= date)
            & (transactions["Категория"] == category)
            ]

        grouped_transactions = filtered_transactions.groupby(pd.Grouper(key="Дата операции", freq="M")).sum()
        reports_logger.info(f"Траты за последние три месяца от {date} по категории {category}")
        return grouped_transactions.to_dict(orient="records")

    except Exception as e:
        reports_logger.error(f"Ошибка: {e}")
        return ""


if __name__ == "__main__":
    result = spending_by_category(config.transactions, "Дом и ремонт", "2021.12.28")
    print(result)
