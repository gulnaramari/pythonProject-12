from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
import requests

from src.utils import (filter_transactions_by_date,
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
        result = read_excel_to_dict_lict(r"../data/operations.xlsx")
        assert result == test_data


@pytest.fixture
def test_transactions():
    return [
        {
            "Дата операции": "17.12.2021 16:28:23",
            "Сумма операции": "-229.00",
            "Категория": "Фастфуд",
            "Описание": "Evo_Kebab Bar",
        },
        {
            "Дата операции": "19.11.2021 11:37:04",
            "Сумма операции": "-271.40",
            "Категория": "Косметика",
            "Описание": "Подружка",
        },
        {
            "Дата операции": "16.11.2021 21:40:11",
            "Сумма операции": "-456.00",
            "Категория": "Аптеки",
            "Описание": "Аптека Вита",
        },
        {
            "Дата операции": "14.11.2021 10:56:53",
            "Сумма операции": "-127.80",
            "Категория": "Супермаркеты",
            "Описание": "Перекрёсток",
        },
        {
            "Дата операции": "09.11.2021 21:03:50",
            "Сумма операции": "-1700.00",
            "Категория": "Развлечения",
            "Описание": "Kassaramblerrbs",
        },
        {
            "Дата операции": "01.08.2021 22:55:33",
            "Сумма операции": "-236.79",
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
         }
    ]


@pytest.mark.parametrize(
    "input_date_str, expected_result",
    [
        (
            "19.11.2021",
            [
                {
                    "Дата операции": "16.11.2021 21:40:11",
                    "Сумма операции": "-456.00",
                    "Категория": "Аптеки",
                    "Описание": "Аптека Вита",
                },
                {
                    "Дата операции": "09.11.2021 21:03:50",
                    "Сумма операции": "-1700.00",
                    "Категория": "Развлечения",
                    "Описание": "Kassaramblerrbs",
                },
                {
                    "Дата операции": "14.11.2021 10:56:53",
                    "Сумма операции": "-127.80",
                    "Категория": "Супермаркеты",
                    "Описание": "Перекрёсток",
                },
            ],
        ),
        (
            "15.08.2021",
            [
                {
                    "Дата операции": "01.08.2021 22:55:33",
                    "Сумма операции": "-236.79",
                    "Категория": "Супермаркеты",
                    "Описание": "Магнит",
                },
            ],
        ),
    ],
)
def test_filter_transactions_by_date(test_transactions, input_date_str, expected_result):
    result = filter_transactions_by_date(test_transactions, input_date_str)
    assert result == expected_result


@patch("src.utils.datetime")
@pytest.mark.parametrize(
    "current_hour, expected_greeting",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_greeting(mock_datetime, current_hour, expected_greeting):
    mock_now = datetime(2023, 6, 20, current_hour, 0, 0)
    mock_datetime.now.return_value = mock_now
    result = greeting()
    assert result == expected_greeting


def test_get_cards_data_empty():
    transactions = []
    expected_result = []
    assert get_cards_data(transactions) == expected_result


def test_get_cards_data_single_transaction():
    transactions = [{"Номер карты": "1234", "Сумма операции": "-100.0", "Кэшбэк": "1.0", "Категория": "Продукты"}]
    expected_result = [{"last_digits": "1234", "total_spent": 100.0, "cashback": 1.0}]
    assert get_cards_data(transactions) == expected_result


def test_get_cards_data_multiple_transactions():
    transactions = [
        {"Номер карты": "1234", "Сумма операции": "-100.0", "Кэшбэк": "1.0", "Категория": "Продукты"},
        {"Номер карты": "1234", "Сумма операции": "-200.0", "Кэшбэк": "2.0", "Категория": "Продукты"},
        {"Номер карты": "5678", "Сумма операции": "-50.0", "Кэшбэк": "0.5", "Категория": "Продукты"},
    ]
    expected_result = [
        {"last_digits": "1234", "total_spent": 300.0, "cashback": 3.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert get_cards_data(transactions) == expected_result


def test_get_cards_data_nan_card_number():
    transactions = [
        {"Номер карты": "1234", "Сумма операции": "-100.0", "Кэшбэк": "1.0", "Категория": "Продукты"},
        {"Номер карты": "nan", "Сумма операции": "-200.0", "Кэшбэк": "2.0", "Категория": "Продукты"},
        {"Номер карты": "5678", "Сумма операции": "-50.0", "Кэшбэк": "0.5", "Категория": "Продукты"},
    ]
    expected_result = [
        {"last_digits": "1234", "total_spent": 100.0, "cashback": 1.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert get_cards_data(transactions) == expected_result


def test_get_cards_data_cashback():
    transactions = [
        {"Номер карты": "1234", "Сумма операции": "-100.0", "Категория": "Продукты"},
        {"Номер карты": "5678", "Сумма операции": "-50.0", "Категория": "Продукты"},
    ]
    expected_result = [
        {"last_digits": "1234", "total_spent": 100.0, "cashback": 1.0},
        {"last_digits": "5678", "total_spent": 50.0, "cashback": 0.5},
    ]
    assert get_cards_data(transactions) == expected_result


def test_get_top_5_transactions_empty():
    transactions = []
    expected_result = []
    assert get_top_5_transactions(transactions) == expected_result


def test_get_top_5_transactions_single_transaction():
    transactions = [
        {
            "Дата операции": "20.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Еда",
            "Описание": "Покупка еды",
        }
    ]
    expected_result = [{"date": "20.06.2023", "amount": "-100.0", "category": "Еда", "description": "Покупка еды"}]
    assert get_top_5_transactions(transactions) == expected_result


def test_get_top_5_transactions_multiple_transactions():
    transactions = [
        {
            "Дата операции": "20.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Еда",
            "Описание": "Покупка еды",
        },
        {
            "Дата операции": "21.06.2023 12:00:00",
            "Сумма операции": "-200.0",
            "Категория": "Транспорт",
            "Описание": "Оплата проезда",
        },
        {
            "Дата операции": "22.06.2023 12:00:00",
            "Сумма операции": "-50.0",
            "Категория": "Развлечения",
            "Описание": "Кино",
        },
        {
            "Дата операции": "23.06.2023 12:00:00",
            "Сумма операции": "-300.0",
            "Категория": "Магазины",
            "Описание": "Покупка одежды",
        },
        {
            "Дата операции": "24.06.2023 12:00:00",
            "Сумма операции": "-20.0",
            "Категория": "Кофе",
            "Описание": "Кофе на вынос",
        },
        {
            "Дата операции": "25.06.2023 12:00:00",
            "Сумма операции": "-400.0",
            "Категория": "Магазины",
            "Описание": "Покупка техники",
        },
    ]
    expected_result = [
        {"date": "25.06.2023", "amount": "-400.0", "category": "Магазины", "description": "Покупка техники"},
        {"date": "23.06.2023", "amount": "-300.0", "category": "Магазины", "description": "Покупка одежды"},
        {"date": "21.06.2023", "amount": "-200.0", "category": "Транспорт", "description": "Оплата проезда"},
        {"date": "20.06.2023", "amount": "-100.0", "category": "Еда", "description": "Покупка еды"},
        {"date": "22.06.2023", "amount": "-50.0", "category": "Развлечения", "description": "Кино"},
    ]
    assert get_top_5_transactions(transactions) == expected_result


def test_get_top_5_transactions_less_than_5():
    transactions = [
        {
            "Дата операции": "20.06.2023 12:00:00",
            "Сумма операции": "-100.0",
            "Категория": "Еда",
            "Описание": "Покупка еды",
        },
        {
            "Дата операции": "21.06.2023 12:00:00",
            "Сумма операции": "-200.0",
            "Категория": "Транспорт",
            "Описание": "Оплата проезда",
        },
    ]
    expected_result = [
        {"date": "21.06.2023", "amount": "-200.0", "category": "Транспорт", "description": "Оплата проезда"},
        {"date": "20.06.2023", "amount": "-100.0", "category": "Еда", "description": "Покупка еды"},
    ]
    assert get_top_5_transactions(transactions) == expected_result


def test_get_top_5_transactions_with_equal_amounts():
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
        {"date": "20.06.2023", "amount": "-100.0", "category": "Еда", "description": "Покупка еды"},
        {"date": "21.06.2023", "amount": "-100.0", "category": "Транспорт", "description": "Оплата проезда"},
        {"date": "22.06.2023", "amount": "-100.0", "category": "Развлечения", "description": "Кино"},
        {"date": "23.06.2023", "amount": "-100.0", "category": "Магазины", "description": "Покупка одежды"},
        {"date": "24.06.2023", "amount": "-100.0", "category": "Кофе", "description": "Кофе на вынос"},
    ]
    assert get_top_5_transactions(transactions) == expected_result


@pytest.fixture
def api_key_currency():
    return "test_api_key"


def test_get_exchange_rates_success(api_key_currency):
    currencies = ["USD", "EUR"]
    expected_result = [{"currency": "USD", "rate": 75.0}, {"currency": "EUR", "rate": 90.0}]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/USD",
            json={"conversion_rates": {"RUB": 75.0}},
        )
        mocker.get(
            f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/EUR",
            json={"conversion_rates": {"RUB": 90.0}},
        )

        assert get_exchange_rates(currencies, api_key_currency) == expected_result


def test_get_exchange_rates_partial_failure(api_key_currency):
    currencies = ["USD", "EUR"]
    expected_result = [{"currency": "USD", "rate": 75.0}, {"currency": "EUR", "rate": None}]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/USD",
            json={"conversion_rates": {"RUB": 75.0}},
        )
        mocker.get(
            f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/EUR", status_code=404, text="Not Found"
        )

        assert get_exchange_rates(currencies, api_key_currency) == expected_result


def test_get_exchange_rates_all_failure(api_key_currency):
    currencies = ["USD", "EUR"]
    expected_result = [{"currency": "USD", "rate": None}, {"currency": "EUR", "rate": None}]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/USD", status_code=500, text="Server Error"
        )
        mocker.get(
            f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/EUR", status_code=500, text="Server Error"
        )

        assert get_exchange_rates(currencies, api_key_currency) == expected_result


@pytest.fixture
def api_key_stocks():
    return "test_api_key"


def test_get_stocks_cost_success(api_key_stocks):
    companies = ["AAPL", "AMZN"]
    expected_result = [{"stock": "AAPL", "price": 150.0}, {"stock": "AMZN", "price": 3000.0}]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=" f"{api_key_stocks}",
            json={"Time Series (Daily)": {"2023-06-19": {"4. close": "150.0"}}},
        )
        mocker.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AMZN&apikey=" f"{api_key_stocks}",
            json={"Time Series (Daily)": {"2023-06-19": {"4. close": "3000.0"}}},
        )

        assert get_stocks_cost(companies, api_key_stocks) == expected_result


def test_get_stocks_cost_partial_failure(api_key_stocks):
    companies = ["AAPL", "AMZN"]
    expected_result = [{"stock": "AAPL", "price": 150.0}, {"stock": "AMZN", "price": None}]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=" f"{api_key_stocks}",
            json={"Time Series (Daily)": {"2023-06-19": {"4. close": "150.0"}}},
        )
        mocker.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AMZN&apikey=" f"{api_key_stocks}",
            status_code=404,
            text="Not Found",
        )

        assert get_stocks_cost(companies, api_key_stocks) == expected_result


def test_get_stocks_cost_all_failure(api_key_stocks):
    companies = ["AAPL", "AMZN"]
    expected_result = [{"stock": "AAPL", "price": None}, {"stock": "AMZN", "price": None}]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=" f"{api_key_stocks}",
            status_code=500,
            text="Server Error",
        )
        mocker.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AMZN&apikey=" f"{api_key_stocks}",
            status_code=500,
            text="Server Error",
        )

        assert get_stocks_cost(companies, api_key_stocks) == expected_result
