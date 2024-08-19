from CBR_currency import get_cbr_currency
from BBR_currency import get_bbr_currency
import gspread


CBR_URL = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req='
CBR_CURRENCY_CODES = [840, 978, 156]

USDRUB_cell = 'J2'
CNYRUB_cell = 'J3'
CNYRUB_BBR_cell = 'J4'

today_CNY_BBR = get_bbr_currency()
today_CBR = get_cbr_currency(CBR_URL, CBR_CURRENCY_CODES)

print(today_CNY_BBR)
print(today_CBR)

CNY_spread = round(today_CBR['CNY'] - today_CNY_BBR['CNY']['buy'], 2)

gc = gspread.oauth()
sh = gc.open('cash')

# fill USDRUB, CNYRUB CBR value
sh.sheet1.update(USDRUB_cell, today_CBR['USD'])
sh.sheet1.update(CNYRUB_cell, today_CBR['CNY'])

# fill CNYRUB BBR value
sh.sheet1.update(CNYRUB_BBR_cell, today_CNY_BBR['CNY']['buy'])

worksheet_list = sh.worksheet('log')
worksheet_list.append_row(['CNYRUB_BBR', # name
                          today_CNY_BBR['CNY']['buy'],  # BBR value
                          CNY_spread,                   # spread
                          today_CNY_BBR['CNY']['date'],  # actual at date
                           today_CNY_BBR['CNY']['time']  # actual at time
                           ]
                          )



