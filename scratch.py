import gspread
from pathlib import Path
from datetime import datetime
from BBR_currency import get_bbr_currency

service_key_file = [i for i in Path('.').rglob("secrets/*service_key*")]

today_CNY_BBR = get_bbr_currency()

today_CNY_BBR_datetime = [today_CNY_BBR['CNY']['date'], today_CNY_BBR['CNY']['time']]
today_CNY_BBR_datetime = "_".join(today_CNY_BBR_datetime)
today_CNY_BBR_datetime = datetime.strptime(today_CNY_BBR_datetime, "%d.%m.%Y_%H:%M:%S")

gc = gspread.service_account(filename=service_key_file[0].absolute())
table = gc.open('cash')
BBR_sheet = table.worksheet('log')
actual_at_datetime = [BBR_sheet.get_all_records()[-1]['actual_at_date'], BBR_sheet.get_all_records()[-1]['time']]
actual_at_datetime = '_'.join(actual_at_datetime)
actual_at_datetime_converted = datetime.strptime(actual_at_datetime, "%d.%m.%Y_%H:%M:%S")
# print(f"{actual_at_date, actual_at_time}")
print(f"{actual_at_datetime}")
print(f"{actual_at_datetime_converted}")

print(f"{today_CNY_BBR_datetime}")

print(actual_at_datetime_converted < today_CNY_BBR_datetime)
