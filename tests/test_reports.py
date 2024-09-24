import pytest
import pandas as pd
from src.reports import spending_by_category
from src.utils import fetch_user_data
import config


result_all = fetch_user_data("../data/operations.xlsx")
result_spending = spending_by_category(result_all, "Супермаркеты", date="31.12.2021")


@pytest.fixture
def fix_reports():
    return result_spending


def test_report(fix_reports):
    assert spending_by_category(result_all, "Переводы", date="31.12.2021") == fix_reports


@pytest.fixture
def test_data():
    data = {
        "Дата операции": [
            "30.12.2021 14:48:25",
            "28.12.2021 18:24:02",
            ],
        "Категория": ["Канцтовары", "Дом и ремонт"],
        "Сумма операции": [550, 17454],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category_correct(test_data):
    """Тестирование функции с указанной датой и категорией "Дом и ремонт"""
    result = spending_by_category(test_data, "Дом и ремонт", "28.12.2021 14:48:25")
    assert (
        len(result) == 14
    )


def test_spending_by_category_no_date(test_data):
    result = spending_by_category(test_data, "Дом и ремонт", )
    assert len(result) == 14


def test_spending_by_category_no_date(test_data):
    result = spending_by_category(test_data, "Канцтовары")
    assert len(result) == 0


def test_spending_by_category_incorrect_date(test_data):
    # Тестирование функции с датой, которой еще нет в данных
    result = spending_by_category(test_data, "Канцтовары", "01.01.2024 00:00:00")
    assert (
        len(result) == 0
    )


def test_spending_by_category_no_transactions(test_data):
    # Тестирование функции с категорией, для которой нет транзакций
    result = spending_by_category(test_data, "Фитнес", "27.12.2021 15:56:23")
    assert len(result) == 0
