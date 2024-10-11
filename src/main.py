import config
from src.reports import spending_by_category
from src.services import analyze_cashback
from src.utils import fetch_user_data
from src.views import main_json, user_choice

# main_page = main_json("2020.12.10 17:50:17", user_choice)
# print(main_page)

df = fetch_user_data(config.PATH_TO_XLSX)
spending_by_category_result = spending_by_category(df, "Супермаркеты", "28.12.2021 13:44:39")
print(spending_by_category_result)

# transactions = df.to_dict('records')
# cashback_analysis_result = analyze_cashback(2020, 12, transactions)
# print(cashback_analysis_result)