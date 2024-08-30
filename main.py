from CBR_currency import get_cbr_currency
from BBR_currency import get_bbr_currency
import gspread
import argparse
from datetime import datetime
import pytz
from pathlib import Path
import os

CBR_URL = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req='
CBR_CURRENCY_CODES = [840, 978, 156]

parser = argparse.ArgumentParser(
    prog='get_currency',
    description='fetch currency from BBR bank and CBR, then fill it to googlesheets',
    epilog="available modes: -u for update sheet, or without args to just print"
)
parser.add_argument('-u', '--update_mode', action='store_true', help='update google sheet')
args = parser.parse_args()
# print(args, args.update_mode)

USDRUB_cell = 'J2'
CNYRUB_cell = 'J3'
CNYRUB_BBR_cell = 'J4'

today_CNY_BBR = get_bbr_currency()
today_CBR = get_cbr_currency(CBR_URL, CBR_CURRENCY_CODES)

CNY_spread = round(today_CBR['CNY'] - today_CNY_BBR['CNY']['buy'], 2)


def update_gsheets(USDRUB_cell, CNYRUB_cell, CNYRUB_BBR_cell, today_CNY_BBR, today_CBR):
    now = datetime.now(pytz.timezone('Europe/Moscow')) # Exact Moscow time, not time of server
    now_date = datetime.strftime(now, "%Y-%m-%d")
    now_time = datetime.strftime(now, "%H:%M:%S")

    # gc = gspread.oauth(
    # credentials_filename='secrets/credentials.json',
    # authorized_user_filename='secrets/authorized_user.json'
    # )

    service_key_file = [i for i in Path('.').rglob("secrets/*service_key*")]
    if len(service_key_file) < 1:
        return print('Something wrong with service key file, please check it! ')

    gc = gspread.service_account(filename=service_key_file[0].absolute())
    sh = gc.open('cash')

    # fill USDRUB, CNYRUB CBR value
    sh.sheet1.update(USDRUB_cell, today_CBR['USD'])
    sh.sheet1.update(CNYRUB_cell, today_CBR['CNY'])

    # fill CNYRUB BBR value
    sh.sheet1.update(CNYRUB_BBR_cell, today_CNY_BBR['CNY']['buy'])

    # update log sheet
    worksheet_list = sh.worksheet('log')
    worksheet_list.append_row(['CNYRUB_BBR',  # name
                               today_CNY_BBR['CNY']['buy'],  # BBR value
                               CNY_spread,  # spread
                               today_CNY_BBR['CNY']['date'],  # actual at date
                               today_CNY_BBR['CNY']['time']  # actual at time

                               ], value_input_option='USER_ENTERED'
                              )
    print(today_CBR)

    worksheet_list = sh.worksheet('CBR_currency_log')
    worksheet_list.append_row([
        today_CBR['USD'],
        today_CBR['CNY'],
        today_CBR['EUR'],
        today_CBR['date'],
        now_date,  # Date of log
        now_time  # time of log
        ]
        , value_input_option='USER_ENTERED'
    )

    print('sheet updated successfully')

if args.update_mode:
    update_gsheets(USDRUB_cell, CNYRUB_cell, CNYRUB_BBR_cell, today_CNY_BBR, today_CBR)
else:
    print(today_CNY_BBR)
    print(today_CBR)
    print(f"CNY spread is: {CNY_spread}")
