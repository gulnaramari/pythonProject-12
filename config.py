import os
from dotenv import load_dotenv
from src.utils import fetch_user_data

PATH_TO_XLSX = os.path.join(os.path.dirname(__file__), 'data', 'operation.xlsx')

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_SP = os.getenv("API_KEY_SP")

input_date_str = "20.03.2020"
transactions = fetch_user_data(r"../data/operations.xlsx")
year = 2020
month = 5
date = "2020.05"
limit = 50
search = "Перевод"
