import pandas as pd
import datetime

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
    """Приветствие пользователя"""
    time_obj = datetime.datetime.now()
    if 6 <= time_obj.hour <= 12:
        return "Доброе утро"
    elif 13 <= time_obj.hour <= 18:
        return "Добрый день"
    elif 19 <= time_obj.hour <= 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
