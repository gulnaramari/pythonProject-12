import json
import pytest
from src.services import analyze_cashback
from src.utils import fetch_user_data

empty_list = []
test_list = fetch_user_data("../data/operations.xlsx")


@pytest.mark.parametrize("year, month, transactions, expected_output", (
    (2020, 5,
        [{"Дата операции": "15.05.2020 14:41:31", "Категория": "Супермаркеты", "Сумма операции": -115.60,
                    "Кэшбэк": 1.156},
         {"Дата операции": "11.05.2020 15:54:32", "Категория": "Аптеки", "Сумма операции": -243.00,
                    "Кэшбэк": 2.43},
         {"Дата операции": "02.05.2020 13:41:39", "Категория": "ЖКХ", "Сумма операции": -2155.05,
                    "Кэшбэк": 21.6},
        ],
        json.dumps({
            "Супермаркеты": 1.156,
            "Аптеки": 2.43,
            "ЖКХ": 21.6,
        }, ensure_ascii=False, indent=4)
    ),
    (2020,
        4,
        [
            {"Дата операции": "21.04.2020 21:27:27", "Категория": "Супермаркеты", "Сумма операции": -105.80,
                "Кэшбэк": 1.06},
            {"Дата операции": "21.04.2020 00:00:00", "Категория": "Транспорт", "Сумма операции": -607.00,
                "Кэшбэк": 6.07},
            {"Дата операции": "18.04.2020 14:22:36", "Категория": "Супермаркеты", "Сумма операции": -709.80,
                "Кэшбэк": 7.09},
            {"Дата операции": "19.04.2020 15:38:24", "Категория": "Транспорт", "Сумма операции": -601.00,
                "Кэшбэк": 6.01},
        ],
        json.dumps({
            "Супермаркеты": 8.15,
            "Транспорт": 12.08
        }, ensure_ascii=False, indent=4)
    ),
    (
        2023, 7,
            [{"Дата операции": "15.07.2023 12:34:56", "Категория": "Транспорт", "Сумма операции": -1500,
                "Кэшбэк": 15},
            {"Дата операции": "15.07.2023 12:34:56", "Категория": "Транспорт", "Сумма операции": -500,
                "Кэшбэк": 5},
            {"Дата операции": "15.07.2023 12:34:56", "Категория": "Развлечения", "Сумма операции": -500,
                "Кэшбэк": 5},
            {"Дата операции": "15.04.2023 12:34:56", "Категория": "Транспорт", "Сумма операции": -1000,
                "Кэшбэк": 10}
        ],
        json.dumps({
            "Транспорт": 20.0,
            "Развлечения": 5.0
        }, ensure_ascii=False, indent=4)
    )
))
def test_analyze_cashback_(year, month, transactions, expected_output):
    result = analyze_cashback(year, month, transactions)
    assert result == expected_output


@pytest.mark.parametrize("year, month, transactions, expected_output", (
    (2020, 5,
        [{"Дата операции": "15.05.2020 14:41:31", "Категория": "Супермаркеты", "Сумма операции": -115.60,
                    "Кэшбэк": None},
         {"Дата операции": "11.05.2020 15:54:32", "Категория": "Аптеки", "Сумма операции": -243.00,
                    "Кэшбэк": None},
        ],
        json.dumps({
            "Супермаркеты": 1.156,
            "Аптеки": 2.43,
          }, ensure_ascii=False, indent=4)
       ),
    )
)
def test_analyze_cashback_(year, month, transactions, expected_output):
    """Тестирование функции с пустым кешбеком"""
    result_ = analyze_cashback(year, month, transactions)
    assert result_ == expected_output


def test_analyze_cashback_empty_date():
    """Тестирование функции с пустым списком транзакций"""
    empty_list = []
    assert analyze_cashback(2022, 2, empty_list) == json.dumps([], indent=4, ensure_ascii=False)
    assert analyze_cashback(2022, 2, []) == "[]"


