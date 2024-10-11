import pytest
import pandas as pd
from src.reports import spending_by_category
import config




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

@pytest.fixture
def sample_data():
    # Пример тестовых данных
    data = {
        "Дата операции": [
            "01.12.2021 12:00:00",
            "15.12.2021 10:30:00",
            "25.12.2021 18:45:00",
            "05.01.2022 08:00:00",
            "20.02.2022 16:20:00",
        ],
        "Категория": ["Продукты", "Продукты", "Транспорт", "Продукты", "Транспорт"],
        "Сумма": [100, 200, 50, 150, 80],
    }
    df = pd.DataFrame(data)
    return df


# def test_spending_by_category_correct(all_reports):
#     """Тестирование функции с указанной датой и категорией "Каршеринг"""
#     result = spending_by_category(all_reports, "Каршеринг", "28.12.2021 14:48:25")
#     assert (
#         len(result) == 93
#     )


def test_spending_by_category_no_date(test_data):
    """Тестирование функции без указанной даты и категорией "Канцтовары"""
    result = spending_by_category(test_data, "Канцтовары")
    assert (len(result) == 0)


def test_spending_by_category_incorrect_date(test_data):
    """Тестирование функции с категорией Канцтовары и с датой, которой еще нет в датафрейме"""
    result = spending_by_category(test_data, "Канцтовары", "01.01.2024 00:00:00")
    assert len(result) == 0



def test_spending_by_category_no_transactions(test_data):
    """Тестирование функции с категорией, для которой нет транзакций"""
    result = spending_by_category(test_data, "Фитнес", "27.12.2021 15:56:23")
    assert len(result) == 0


def test_spending_by_category_no(test_data):
    """Тестирование функции с категорией, которой нет """
    result = spending_by_category(test_data, "Продукты")
    assert len(result) == 0





def test_spending_by_category_with_date(sample_data):
    # Тестирование функции с указанной датой и категорией "Продукты"
    result = spending_by_category(sample_data, "Продукты", "30.12.2021 17:50:30")
    assert (
        len(result) == 2
    )  # Ожидается 2 строки, так как только две операции с категорией
    # "Продукты" за последние три месяца от указанной даты


def test_spending_by_category_no_d(sample_data):
    result = spending_by_category(sample_data, "Продукты")
    assert len(result) == 0  # Ожидаем три строки, соответствующие категории "Продукты"


def test_spending_by_category_future(sample_data):
    # Тестирование функции с будущей датой
    result = spending_by_category(sample_data, "Продукты", "01.01.2023 00:00:00")
    assert (
        len(result) == 0
    )  # Ожидается 0 строк, так как нет операций с категорией "Продукты" за последние три месяца от будущей даты


def test_spending_by_category_no_tr(sample_data):
    # Тестирование функции с категорией, для которой нет транзакций
    result = spending_by_category(sample_data, "Здоровье", "30.12.2021 17:50:30")
    assert len(result) == 0  # Ожидается 0 строк, так как нет транзакций с категорией "Здоровье"


if __name__ == "__main__":
    pytest.main()
