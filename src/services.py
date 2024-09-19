import datetime
import json
import logging
import os

import pandas as pd

PATH_TO_FILE = os.path.join(os.path.dirname(__file__), "../data", "operations.xlsx")
df = pd.read_excel(PATH_TO_FILE)
df.columns = [
    "Transaction date",
    "Payment date",
    "Card number",
    "Status",
    "Transaction amount",
    "Transaction currency",
    "Payment amount",
    "Payment currency",
    "Cashback",
    "Category",
    "MCC",
    "Description",
    "Bonuses (including cashback)",
    "Rounding to the investment bank",
    "The amount of the operation with rounding",
]
edited_df = df.drop(
    [
        "Payment date",
        "Card number",
        "Status",
        "Transaction currency",
        "Payment amount",
        "Payment currency",
        "Cashback",
        "Category",
        "MCC",
        "Description",
        "Bonuses (including cashback)",
        "Rounding to the investment bank",
        "The amount of the operation with rounding",
    ],
    axis=1,
)

data_dict = edited_df.to_dict(orient="records")
services_logger = logging.getLogger("services")
file_handler = logging.FileHandler("../logs/services.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.INFO)


def investment_bank(month: str, transactions: list[dict[str, [str | float]]], limit: int):
    """Функция расчитывающая сумму отложенную в инвесткопилку для каждой транзакции"""
    transaction_list_for_month = []
    for element in transactions:
        if editing_date_format(element["Transaction date"]) == month:
            transaction_list_for_month.append(element)
    services_logger.info("Сортировка транзакций завершена")
    if transaction_list_for_month == []:
        print("Некорректный формат даты")
        services_logger.error("Неверный формат даты")
        return []
    else:
        for transaction in transaction_list_for_month:
            if abs(transaction["Transaction amount"]) <= limit and abs(transaction["Transaction amount"]) % limit != 0:
                amount_to_investbank = limit - abs(transaction["Transaction amount"])
                amount_with_rounding = abs(transaction["Transaction amount"]) + amount_to_investbank
                transaction["Rounding to the investment bank"] = round(amount_to_investbank, 2)
                transaction["The amount of the operation with rounding"] = amount_with_rounding
            elif (
                abs(transaction["Transaction amount"]) >= limit and abs(transaction["Transaction amount"]) % limit != 0
            ):
                amount_to_investbank = limit - abs(transaction["Transaction amount"]) % limit
                amount_with_rounding = abs(transaction["Transaction amount"]) + amount_to_investbank
                transaction["Rounding to the investment bank"] = round(amount_to_investbank, 2)
                transaction["The amount of the operation with rounding"] = amount_with_rounding
            else:
                transaction["Rounding to the investment bank"] = 0
                transaction["The amount of the operation with rounding"] = transaction["Transaction amount"]
        services_logger.info("Расчёт кэшбека завершён успешно")
        return json.dumps(transaction_list_for_month, indent=4)


print(investment_bank("2021-12", data_dict, 50))
