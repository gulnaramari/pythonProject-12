from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
import unittest
import pandas as pd
import pytest
import requests


from src.utils import (filter_transactions_by_date, fetch_user_data,
                       greeting_twenty_four_hours, analyze_dict_user_card,
                       fetch_currency_rates_values, fetch_stock_prices_values,
                       top_user_transactions)

ROOT_PATH = Path(__file__).resolve().parent.parent


def test_get_data_from_xlsx():
    test_data = [
        {
            "Дата операции": "28.12.2021 18:42:21",
            "Сумма операции": "-257,89",
            "Категория": "Каршеринг",
            "Описание": "Ситидрайв",
        },
        {
            "Дата операции": "18.12.2021 16:53:16",
            "Сумма операции": "-176,00",
            "Категория": "Топливо",
            "Описание": "ЛУКОЙЛ",
        },
    ]
    df = pd.DataFrame(test_data)
    with patch("pandas.read_excel", return_value=df):
        result = fetch_user_data(r"../data/operations.xlsx")
        assert result == test_data


@pytest.fixture
def test_transactions():
    return [
        {
            "Дата операции": "14.11.2021 10:56:53",
            "Сумма операции": 127.80,
            "Категория": "Супермаркеты",
            "Описание": "Перекрёсток",
        },
        {
            "Дата операции": "19.11.2021 11:37:04",
            "Сумма операции": 271.40,
            "Категория": "Косметика",
            "Описание": "Подружка",
        },
        {
            "Дата операции": "16.11.2021 21:40:11",
            "Сумма операции": 456.00,
            "Категория": "Аптеки",
            "Описание": "Аптека Вита",
        },
        {
            "Дата операции": "09.11.2021 21:03:50",
            "Сумма операции": 1700.00,
            "Категория": "Развлечения",
            "Описание": "Kassaramblerrbs",
        },
        {
            "Дата операции": "01.08.2021 22:55:33",
            "Сумма операции": 236.79,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
         },
        {
            "Дата операции": "19.08.2021 21:22:58",
            "Сумма операции": 226.70,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
        },
    ]


@pytest.mark.parametrize(
    "input_date, expected_result",
    [
        (
            "20.11.2021",
            [
                {
                    "Дата операции": "14.11.2021 10:56:53",
                    "Сумма операции": 127.80,
                    "Категория": "Супермаркеты",
                    "Описание": "Перекрёсток",
                },
                {
                    "Дата операции": "19.11.2021 11:37:04",
                    "Сумма операции": 271.40,
                    "Категория": "Косметика",
                    "Описание": "Подружка",
                },
                {
                    "Дата операции": "16.11.2021 21:40:11",
                    "Сумма операции": 456.00,
                    "Категория": "Аптеки",
                    "Описание": "Аптека Вита",
                },
                {
                    "Дата операции": "09.11.2021 21:03:50",
                    "Сумма операции": 1700.00,
                    "Категория": "Развлечения",
                    "Описание": "Kassaramblerrbs",
                },
            ],
        ),
        (
            "20.08.2021",
            [
                {
                    "Дата операции": "01.08.2021 22:55:33",
                    "Сумма операции": 236.79,
                    "Категория": "Супермаркеты",
                    "Описание": "Магнит",
                },
                {
                   "Дата операции": "19.08.2021 21:22:58",
                   "Сумма операции": 226.70,
                   "Категория": "Супермаркеты",
                   "Описание": "Магнит",
                },
            ],
        ),
    ],
)
def test_filter_transactions_by_date(test_transactions, input_date, expected_result):
    result = filter_transactions_by_date(test_transactions, input_date)
    assert result == expected_result


@patch("src.utils.datetime")
@pytest.mark.parametrize(
    "actual_time, expected_greeting",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_greeting_twenty_four_hours(mock_datetime, actual_time, expected_greeting):
    mock_now = datetime(2021, 2, 9, actual_time, 0, 0)
    mock_datetime.now.return_value = mock_now
    result = greeting_twenty_four_hours()
    assert result == expected_greeting


def test_analyze_dict_user_card_one_correct():
    transactions = [{"Номер карты": "*4556", "Сумма операции": "-1411.40", "Кэшбэк": "70", "Категория": "Ж/д билеты"}]
    expected_result = [{"last_digits": "*4556", "total_spent": 1411.40, "cashback": 70.0}]
    assert analyze_dict_user_card(transactions) == expected_result


def test_analyze_dict_user_card_no():
    transactions = []
    expected_result = []
    assert analyze_dict_user_card(transactions) == expected_result


def test_analyze_dict_user_card_transactions():
    transactions = [
        {"Номер карты": "*1234", "Сумма операции": "-200.0", "Кэшбэк": "2.0", "Категория": "Продукты"},
        {"Номер карты": "*7197", "Сумма операции": "-108.00", "Кэшбэк": "1.08", "Категория": "Фастфуд"},
    ]
    expected_result = [
        {"last_digits": "*1234", "total_spent": 200.0, "cashback": 2.0},
        {"last_digits": "*7197", "total_spent": 108.0, "cashback": 1.08},
    ]
    assert analyze_dict_user_card(transactions) == expected_result


def test_analyze_dict_user_card_no_card_number():
    transactions = [
        {"Номер карты": "", "Сумма операции": 200.0, "Кэшбэк": 2.0, "Категория": "Продукты"},
             ]
    expected_result = []
    assert analyze_dict_user_card(transactions) == expected_result


def test_analyze_dict_user_card_cashback():
    transactions = [
        {"Номер карты": "1234", "Сумма операции": "-100.0", "Категория": "Продукты"},
        {"Номер карты": "5678", "Сумма операции": "-50.0", "Категория": "Продукты"},
    ]
    expected_result = [
        {"last_digits": "1234", "total_spent": 100.0, "cashback": 1.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert analyze_dict_user_card(transactions) == expected_result


def test_top_user_transactions_empty():
    transactions = []
    expected_result = []
    assert top_user_transactions(transactions) == expected_result


def test_top_user_transactions_one():
    transactions = [
        {
            "Дата операции": "20.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Еда",
            "Описание": "Покупка еды",
        }
    ]
    expected_result = [{"Дата операции": "20.06.2023", "Сумма операции": "-100.0", "Категория": "Еда", "Описание": "Покупка еды"}]
    assert top_user_transactions(transactions) == expected_result



def test_top_user_transactions_all():
    transactions = [
        {
            "Дата операции": "18.09.2021 15:54:33",
            "Сумма операции": 1375.46,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
        },
        {
            "Дата операции": "06.03.2018 12:11:25",
            "Сумма операции": 310.0,
            "Категория": "Фастфуд",
            "Описание": "OOO Frittella"
        },
        {
            "Дата операции": "01.09.2021 14:51:14",
            "Сумма операции": 5990.0,
            "Категория": "Каршеринг",
            "Описание": "Ситидрайв",
        },
        {
            "Дата операции": "20.05.2021 11:05:22",
            "Сумма операции": 28626.0,
            "Категория": "Турагентства",
            "Описание": "AviaKassa.com",
        },
        {
            "Дата операции": "05.06.2021 12:01:35",
            "Сумма операции": 5000.00,
            "Категория": "Турагентства",
            "Описание": "Aeroport Sochi Sector A2",
        },
        {
            "Дата операции": "08.03.2018 20:12:02",
            "Сумма операции": 1194.00,
            "Категория": "Одежда и обувь",
            "Описание": "Kontsept Klub",
        }
    ]
    expected_result = [
        {
            "Дата операции": "20.05.2021",
            "Сумма операции": 28626.0,
            "Категория": "Турагентства",
            "Описание": "AviaKassa.com",
        },
        {
            "Дата операции": "01.09.2021",
            "Сумма операции": 5990.0,
            "Категория": "Каршеринг",
            "Описание": "Ситидрайв",
        },
        {
            "Дата операции": "05.06.2021",
            "Сумма операции": 5000.00,
            "Категория": "Турагентства",
            "Описание": "Aeroport Sochi Sector A2",
        },
        {
            "Дата операции": "18.09.2021",
            "Сумма операции": 1375.46,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
        },
        {
            "Дата операции": "08.03.2018",
            "Сумма операции": 1194.00,
            "Категория": "Одежда и обувь",
            "Описание": "Kontsept Klub",
        }
    ]
    assert top_user_transactions(transactions) == expected_result


def test_top_user_transactions_equal_amounts():
    transactions = [
        {
            "Дата операции": "20.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Еда",
            "Описание": "Покупка еды",
        },
        {
            "Дата операции": "21.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Транспорт",
            "Описание": "Оплата проезда",
        },
        {
            "Дата операции": "22.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Развлечения",
            "Описание": "Кино",
        },
        {
            "Дата операции": "23.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Магазины",
            "Описание": "Покупка одежды",
        },
        {
            "Дата операции": "24.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Кофе",
            "Описание": "Кофе на вынос",
        },
        {
            "Дата операции": "25.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Магазины",
            "Описание": "Покупка техники",
        },
    ]
    expected_result = [
        {"Дата операции": "20.06.2023", "Сумма операции": "-100.0", "Категория": "Еда", "Описание": "Покупка еды"},
        {"Дата операции": "21.06.2023", "Сумма операции": "-100.0", "Категория": "Транспорт", "Описание": "Оплата проезда"},
        {"Дата операции": "22.06.2023", "Сумма операции": "-100.0", "Категория": "Развлечения", "Описание": "Кино"},
        {"Дата операции": "23.06.2023", "Сумма операции": "-100.0", "Категория": "Магазины", "Описание": "Покупка одежды"},
        {"Дата операции": "24.06.2023", "Сумма операции": "-100.0", "Категория": "Кофе", "Описание": "Кофе на вынос"},
    ]
    assert top_user_transactions(transactions) == expected_result


class TestFetchCurrencyRates(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_currency_rates_values_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        result = fetch_currency_rates_values(["EUR"])

        expected = []
        self.assertEqual(result, expected)


@patch("requests.get")
def test_fetch_stock_prices(mock_get):
    """Тестирование функции получения данных об акциях из списка S&P500"""

    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": 210.00}}

    list_stocks = ["AAPL"]

    result = fetch_stock_prices_values(list_stocks)
    expected = [
        {"stock": "AAPL", "price": 210.00},
    ]
    assert result == expected
