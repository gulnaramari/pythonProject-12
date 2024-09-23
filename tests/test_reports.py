import pytest
import pandas as pd
from src.reports import spending_by_category


@pytest.fixture
def test_data():
    data = {
        "Дата операции": [
            "30.12.2021 14:48:25",
            "12.10.2021 13:22:20",
            "25.12.2021 18:45:00",
            "05.01.2022 08:00:00",
            "28.12.2021 18:24:02",
            "23.12.2021 22:33:11"
        ],
        "Категория": ["Канцтовары", "Электроника и техника", "Транспорт", "Продукты", "Дом и ремонт", "Каршеринг"],
        "Сумма": [349, 20629, 50, 150, 1840, 1.51],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category_correct(test_data):
    # Тестирование функции с указанной датой и категорией "Канцтовары""
    result = spending_by_category(test_data, "Канцтовары", "30.12.2021 14:48:25")
    assert (
        len(result) == 0
    )


def test_spending_by_category_no_date(test_data):
    result = spending_by_category(test_data, "Продукты")
    assert len(result) == 0


def test_spending_by_category_incorrect_date(test_data):
    # Тестирование функции с датой, которой еще нет в данных
    result = spending_by_category(test_data, "Продукты", "01.01.2024 00:00:00")
    assert (
        len(result) == 0
    )


def test_spending_by_category_no_transactions(test_data):
    # Тестирование функции с категорией, для которой нет транзакций
    result = spending_by_category(test_data, "Фитнес", "27.12.2021 15:56:23")
    assert len(result) == 0
