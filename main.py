from CBR_currency import get_cbr_currency
from BBR_currency import get_bbr_currency
import gspread
import argparse
from datetime import datetime
from datetime import date
import pytz
from pathlib import Path

# def is_update_needed():


if __name__ == "__main__":
    CBR_URL = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req='
    CBR_CURRENCY_CODES = [840, 978, 156]

    USDRUB_cell = 'J2'
    CNYRUB_cell = 'J3'
    CNYRUB_BBR_cell = 'J4'

    parser = argparse.ArgumentParser(
        prog='get_currency',
        description='fetch currency from BBR bank and CBR, then fill it to googlesheets',
        epilog="available modes: -u for update sheet, or without args to just print"
    )
    parser.add_argument('-u', '--update_mode', action='store_true', help='update google sheet')
    args = parser.parse_args()
    # print(args, args.update_mode)
    service_key_file = [i for i in Path('.').rglob("secrets/*service_key*")]
    if len(service_key_file) < 1:
        print('Something wrong with service key file, please check it! ')

    now = datetime.now(pytz.timezone('Europe/Moscow'))  # Exact Moscow time, not time of server
    now_date = date.today()
    now_time = datetime.strftime(now, "%H:%M:%S")

    gc = gspread.service_account(filename=service_key_file[0].absolute())
    table = gc.open('cash')
    # sheets
    CBR_sheet = table.worksheet('CBR_currency_log')
    BBR_sheet = table.worksheet('log')
    main_sheet = table.worksheet('total')

    last_actual_at = datetime.strptime(CBR_sheet.get_all_records()[-1]['actual_at_date'], "%d.%m.%Y").date()
    last_CNYRUB_CBR = CBR_sheet.get_all_records()[-1]['CNYRUB'] / 10000

    today_CNY_BBR = get_bbr_currency()
    today_CBR = get_cbr_currency(CBR_URL, CBR_CURRENCY_CODES)

    # convert to datetime to compare dates BBR with last row google sheets
    today_CNY_BBR_datetime = [today_CNY_BBR['CNY']['date'], today_CNY_BBR['CNY']['time']]
    today_CNY_BBR_datetime = "_".join(today_CNY_BBR_datetime)
    today_CNY_BBR_datetime = datetime.strptime(today_CNY_BBR_datetime, "%d.%m.%Y_%H:%M:%S")

    # get values from google sheet, then convert to datetime
    last_BBR_row = BBR_sheet.get_all_records()[-1]
    actual_at_datetime = [last_BBR_row['actual_at_date'], last_BBR_row['time']]
    actual_at_datetime = '_'.join(actual_at_datetime)
    actual_at_datetime = datetime.strptime(actual_at_datetime, "%d.%m.%Y_%H:%M:%S")

    last_CNYRUB_BBR = last_BBR_row['CNYRUB'] / 100

    # Debug
    # print(last_actual_at_time, actual_at_time)
    # print(last_actual_at_time > actual_at_time)

    CNY_spread = round(today_CBR['CNY'] - today_CNY_BBR['CNY']['buy'], 2)

    # print(f">>>> {actual_at_datetime, today_CNY_BBR_datetime}")

    print('_' * 20)
    if (actual_at_datetime < today_CNY_BBR_datetime) and (last_CNYRUB_BBR != today_CNY_BBR['CNY']['buy']):
        BBR_sheet.append_row(['CNYRUB_BBR',  # name
                              today_CNY_BBR['CNY']['buy'],  # BBR value
                              CNY_spread,  # spread
                              today_CNY_BBR['CNY']['date'],  # actual at date
                              today_CNY_BBR['CNY']['time']  # actual at time
                              ], value_input_option='USER_ENTERED'
                             )

        main_sheet.update(CNYRUB_BBR_cell, today_CNY_BBR['CNY']['buy'])

        print('BBR sheet updated successfully ')

    else:

        print('BBR sheet is up to date, no update needed.')
    print('\n')

    # if last_actual_at != now_date:
    # print(f">>>>> {last_CNYRUB_CBR, today_CBR['CNY']}")
    if last_CNYRUB_CBR != today_CBR['CNY']:
        now_date = datetime.strftime(now, "%Y-%m-%d")
        now_time = datetime.strftime(now, "%H:%M:%S")

        # fill USDRUB, CNYRUB CBR value
        main_sheet.update(USDRUB_cell, today_CBR['USD'])
        main_sheet.update(CNYRUB_cell, today_CBR['CNY'])
        print('main sheet updated successfully')

        # Fill CBR log
        CBR_sheet.append_row([
            today_CBR['USD'],
            today_CBR['CNY'],
            today_CBR['EUR'],
            today_CBR['date'],
            now_date,  # Date of log
            now_time  # time of log
        ]
            , value_input_option='USER_ENTERED'
        )

        print('CBR sheet updated successfully')
    else:
        print('Main and CBR sheets are up to date.')
        print('_' * 20)

    # is_update_needed(USDRUB_cell, CNYRUB_cell, CNYRUB_BBR_cell)

    # if args.update_mode:
    #     update_gsheets(USDRUB_cell, CNYRUB_cell, CNYRUB_BBR_cell, today_CNY_BBR, today_CBR)
    # else:
    print(today_CNY_BBR)
    print(today_CBR)
    print(f"CNY spread is: {CNY_spread}")
