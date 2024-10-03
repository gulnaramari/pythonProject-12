from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import unittest
import pandas as pd
import pytest


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
    input_date = "14.02.22 12:00:00"
    with pytest.raises(ValueError):
        mod_date(input_date)


def test_get_data_empty():
    """функция обрабатывает исключение при неправильном вводе"""
    input_date = ""
    with pytest.raises(ValueError):
        mod_date(input_date)


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


def test_get_expenses_cards(test_transactions):
    result = analyze_dict_user_card(test_transactions)
    assert result[0] == {"last_digits": "*7197", "total spent": 1500, "cashback": 15.0}
    assert result[1] == {"last_digits": "*4556", "total spent": 2000, "cashback": 20.0}


def test_top_user_transactions_sample():
    transactions = [
        {
            "Дата операции": "18.09.2021 15:54:33",
            "Сумма операции": 1375.46,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
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

