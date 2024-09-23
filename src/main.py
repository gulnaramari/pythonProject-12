import pandas as pd

import config
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import analyze_cashback
from src.views import main_json, user_choice


main_page = main_json(config.input_date_str, user_choice, config.API_KEY, config.API_KEY_SP)
print(main_page)

cashback_analysis_result = analyze_cashback(config.transactions, config.year, config.month)
print(cashback_analysis_result)

df = pd.read_excel(r"../data/operations.xls")
spending_by_category_result = spending_by_category(df, "Супермаркеты", "2020.05.20")
print(spending_by_category_result)
