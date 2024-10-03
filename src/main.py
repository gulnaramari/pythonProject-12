import pandas as pd

import config
from src.reports import spending_by_category
from src.services import analyze_cashback
from src.views import main_json, user_choice

main_page = main_json(config.input_date, user_choice)
print(main_page)

cashback_analysis_result = analyze_cashback(config.year, config.month, config.transactions)
print(cashback_analysis_result)


df = pd.read_excel(r"../data/operations.xlsx")
spending_by_category_result = spending_by_category(df, "Супермаркеты", "28.12.2021 13:44:39")
print(spending_by_category_result)
