import pytest
import pandas as pd
from src.reports import spending_by_category
import config


result_all = config.transactions
result_spending = spending_by_category(result_all, "Супермаркеты", date="31.12.2021")


@pytest.fixture
def all_reports():
    return result_all


@pytest.fixture
def test_report(all_reports):
    return result_spending


@pytest.fixture
def test_data():
    data = {
        "Дата операции": [
            "30.12.2021 14:48:25",
            "30.12.2021 19:06:39",
            "30.12.2021 19:18:22",
            "28.12.2021 18:24:02",
            ],
        "Категория": ["Каршеринг", "Каршеринг", "Канцтовары", "Дом и ремонт"],
        "Сумма операции": [7.07, 1.32, 349.0, 1840.0],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category_correct(all_reports):
    """Тестирование функции с указанной датой и категорией "Каршеринг"""
    result = spending_by_category(all_reports, "Каршеринг", "28.12.2021 14:48:25")
    assert (
        len(result) == 0
    )


def test_spending_by_category_no_date(test_data):
    result = spending_by_category(test_data, "Канцтовары")
    assert (len(result) == 0)


def test_spending_by_category_incorrect_date(test_data):
    # Тестирование функции с датой, которой еще нет в данных
    result = spending_by_category(test_data, "Канцтовары", "01.01.2024 00:00:00")
    assert len(result) == 0



def test_spending_by_category_no_transactions(test_data):
    # Тестирование функции с категорией, для которой нет транзакций
    result = spending_by_category(test_data, "Фитнес", "27.12.2021 15:56:23")
    assert len(result) == 0



def test_spending_by_category_with_date(test_data):
    result = spending_by_category(test_data, "Супермаркеты", "31.12.2021 19:06:39")
    assert len(result) == 5



def test_spending_by_category_no(test_data):
    result = spending_by_category(test_data, "Продукты")
    assert len(result) == 0


def test_spending_by_category_future(test_data):
    # Тестирование функции с будущей датой
    result = spending_by_category(test_data, "Транспорт", "01.01.2023 00:00:00")
    assert len(result) == 0



def test_spending_by_category_transaction(test_data):
    # Тестирование функции с категорией, для которой есть транзакция
    result = spending_by_category(test_data, "Каршеринг", "27.12.2021 10:42:40")
    assert len(result) == 3


def test_spending_by_category_no_tr(test_data):
    # Тестирование функции с категорией, для которой нет транзакций
    result = spending_by_category(test_data, "Кар", "27.12.2021 10:42:40")
    assert len(result) == 0
