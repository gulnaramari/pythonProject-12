import logging
import datetime

logger = logging.getLogger("views.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(filename)s: %(levelname)s: %(message)s",
    filename="../logs/utils.log",
    filemode="w",
)


def filter_by_date(date: str, all_data: list) -> list:
    """Фильтрация словарей по заданной дате"""
    list_actual = []
    logger.info("Начало работы")
    if date == "":
        return list_actual
    year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
    date_obj = datetime.datetime(year, month, day)
    for i in all_data:
        if i["Дата платежа"] == "nan" or type(i["Дата платежа"]) is float:
            continue
        elif (
                date_obj
                >= datetime.datetime.strptime(str(i["Дата платежа"]), "%d.%m.%Y")
                >= date_obj - datetime.timedelta(days=day - 1)
        ):
            list_actual.append(i)
    logger.info("Конец работы ")
    return list_actual

