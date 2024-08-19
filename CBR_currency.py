from typing import List
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


def get_cbr_currency(url: str,
                     currency_codes: List[int]) -> dict:
    cbr_currency_dct = {}

    req = requests.get(url)
    soup = BeautifulSoup(req.text.encode("windows-1251"), 'xml')

    cbr_tree = ET.fromstring(req.text)

    all_currency = soup.findAll('Valute')

    for i in all_currency:
        if int(i.find('NumCode').text) in currency_codes:
            currency_name = i.find('CharCode').text
            currency_value = i.find('Value').text

            # replace coma to dot
            currency_value = currency_value.replace(',', '.')

            cbr_currency_dct[currency_name] = float(currency_value)

    return cbr_currency_dct
