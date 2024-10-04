import os
from dotenv import load_dotenv
from src.utils import fetch_user_data, data_to_list
import pytest

PATH_TO_XLSX = os.path.join(os.path.dirname(__file__), 'data', 'operation.xlsx')

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_SP = os.getenv("API_KEY_SP")

input_date = "28.12.2020 17:50:17"
transactions = fetch_user_data(r"../data/operations.xlsx")
data = data_to_list(r"../data/operations.xlsx")
year = 2020
month = 12



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
