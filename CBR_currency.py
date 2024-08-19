from typing import List
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import datetime

def get_cbr_currency(url: str,
                     currency_codes: List[int]) -> dict:
    cbr_currency_dct = {}

    req = requests.get(url)
    soup = BeautifulSoup(req.text.encode("windows-1251"), 'xml')


    all_currency = soup.findAll('Valute')
    actual_date = ''.join([i.get('Date') for i in soup.find_all('ValCurs')])
    # actual_date = datetime.strptime(actual_date, '%d.%m.%Y')
    cbr_currency_dct['date'] = actual_date

    for i in all_currency:
        if int(i.find('NumCode').text) in currency_codes:
            currency_name = i.find('CharCode').text
            currency_value = i.find('Value').text

            # replace coma to dot
            currency_value = currency_value.replace(',', '.')

            cbr_currency_dct[currency_name] = float(currency_value)

    return cbr_currency_dct
