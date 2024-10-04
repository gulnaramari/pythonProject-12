from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import unittest
import pandas as pd
import pytest
import config


from src.utils import (mod_date, fetch_user_data,
                       greeting_twenty_four_hours, analyze_dict_user_card,
                       fetch_currency_rates_values, fetch_stock_prices_values,
                       top_user_transactions)



def test_get_data_correct():
    """Проверяем, что функция корректно обрабатывает  ввод"""
    input_date = "27.12.2021 10:42:40"
    expected_output = datetime(2021, 12, 27, 10, 42, 40)
    assert mod_date(input_date) == expected_output


def test_get_data_wrong():
    """функция обрабатывает исключение при неправильном вводе"""
    input_date = "140222 120000"
    with pytest.raises(ValueError):
        mod_date(input_date)


def test_get_data_empty():
    """функция обрабатывает исключение при пустом вводе"""
    empty_date = ""
    with pytest.raises(ValueError):
        mod_date(empty_date)


def test_get_greeting_1():
    with pytest.raises(TypeError):
        with patch("datetime.datetime.now") as mock_now:
            mock_now.return_value = datetime(2022, 4, 1, 10, 0, 0)
            assert greeting_twenty_four_hours() == "Доброе утро"


def test_get_greeting_2():
    with pytest.raises(TypeError):
        with patch("datetime.datetime.now") as mock_now:
            mock_now.return_value = datetime(2023, 4, 1, 19, 0, 0)
            assert greeting_twenty_four_hours() == "Добрый вечер"

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


@pytest.fixture
def test_transactions():
    return pd.DataFrame({"Номер карты": ["*7197", "*4556"], "Сумма платежа": [-1500, -2000]})


def test_analyze_dict_user_card(test_transactions):
    result = analyze_dict_user_card(test_transactions)
    assert result == [
        {"last_digits": "*4556", "total_spent": 2000, "cashback": 20.0},
        {"last_digits": "*7197", "total_spent": 1500, "cashback": 15.0},
    ]


@pytest.fixture
def empty_transactions():
    return pd.DataFrame({"Номер карты": ["", "*4556"], "Сумма платежа": [-190000, -2000]})


def test_analyze_dict_user_card_empty(empty_transactions):
    result = analyze_dict_user_card(empty_transactions)
    assert result == [
        {"last_digits": "*4556", "total_spent": 2000, "cashback": 20.0},
    ]


@pytest.fixture
def test_top():
    return pd.DataFrame({"Дата операции":
                             ["09.11.2021 21:03:50", "01.08.2021 22:55:33",
                              "16.11.2021 21:40:11", "19.11.2021 11:37:04",
                              "17.12.2021 16:28:23", "28.12.2021 18:42:21"],
                         "Сумма операции":
                             [-1700.0, -400.0, -456.0, -17500.0, -120.0, -280.0],
                         "Категория":
                             ["Каршеринг", "Топливо", "Фастфуд", "Развлечения", "Супермаркеты", "Транспорт"],
                         "Описание":
                             ["Ситидрайв", "ЛУКОЙЛ", "Evo_Kebab Bar", "Kassaramblerrbs",
                              "Магнит", "Такси"]
                         })


def test_top_user_transactions_sample(test_top):
    result = top_user_transactions(test_top)
    assert result == [
        {
            "Дата операции": "19.11.2021 11:37:04",
            "Сумма операции": -17500.0,
            "Категория": "Развлечения",
            "Описание": "Kassaramblerrbs"
        },
        {
            "Дата операции": "09.11.2021 21:03:50",
            "Сумма операции": -1700.0,
            "Категория": "Каршеринг",
            "Описание": "Ситидрайв"
        },
        {
            "Дата операции": "16.11.2021 21:40:11",
            "Сумма операции": -456.0,
            "Категория": "Фастфуд",
            "Описание": "Evo_Kebab Bar"
        },
        {
            "Дата операции": "01.08.2021 22:55:33",
            "Сумма операции": -400.0,
            "Категория": "Топливо",
            "Описание": "ЛУКОЙЛ"
        },
        {
            "Дата операции": "28.12.2021 18:42:21",
            "Сумма операции": -280.0,
            "Категория": "Транспорт",
            "Описание": "Такси"
        }
    ]

