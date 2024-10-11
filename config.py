import os

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
PATH_TO_XLSX = os.path.join(DATA_DIR, 'operations.xlsx')

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_SP = os.getenv("API_KEY_SP")


#
# @pytest.fixture
# def test_data():
#     data_ = {
#         "Дата операции": [
#             "30.12.2021 14:48:25",
#             "28.12.2021 18:24:02",
#             ],
#         "Категория": ["Канцтовары", "Дом и ремонт"],
#         "Сумма операции": [550, 17454],
#     }
#     df = pd.DataFrame(data_)
#     return df
