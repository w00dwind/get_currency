import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def get_bbr_currency():
    CNY_exchange_rates = {}

    # url = 'https://bbr.ru/'
    # req = requests.get(url)
    # soup = BeautifulSoup(req, 'html')

    cookies = {
        '_ym_uid': '1699377423370585185',
        '_ym_d': '1715009921',
        '_ga': 'GA1.2.1310970945.1715009921',
        'city_slug': 'moskva',
        'city_name': '%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,nl;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        # 'Cookie': '_ym_uid=1699377423370585185; _ym_d=1715009921; _ga=GA1.2.1310970945.1715009921; city_slug=moskva; city_name=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0; _ym_isad=1; _gid=GA1.2.1617483879.1723967211; _gat_gtag_UA_106148749_1=1',
        'Current-Locale': 'ru',
        'Origin': 'https://bbr.ru',
        'Referer': 'https://bbr.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    json_currency = {
        'query': 'query InternetBankRateList($range: InputRateRange) {\n  rates: internetBankRates(range: $range) {\n    elements {\n      id\n      rateType\n      fromCurrency {\n        code\n      }\n      toCurrency {\n        code\n      }\n      buyRate\n      sellRate\n      lot\n    }\n  }\n}',
        'variables': {
            'rateType': 'INTERNET_BANK_EXCHANGE',
        },
    }

    json_data_actual_at = {
    'query': 'query RatesList($rateType: RateTypeEnum, $citySlug: String, $range: InputRateRange, $officeId: Int) {\n  rates(\n    noPagination: true\n    rateType: $rateType\n    citySlug: $citySlug\n    officeId: $officeId\n    range: $range\n  ) {\n    actualAt\n    elements {\n      id\n      rateType\n      fromCurrency {\n        code\n      }\n      toCurrency {\n        code\n      }\n      buyRate\n      buyRateStatus\n      sellRate\n      sellRateStatus\n      lot\n    }\n  }\n}',
    'variables': {
        'rateType': 'CASHLESS_EXCHANGE',
        'citySlug': 'moskva',
        'officeId': 2,
    },
}
    try:
        response_actual_at = requests.post('https://bbr.ru/graphql/',
                                           cookies=cookies,
                                           headers=headers,
                                           json=json_data_actual_at).json()
        actual_at = response_actual_at['data']['rates']['actualAt']
        actual_at = datetime.strptime(actual_at, '%Y-%m-%d %H:%M:%S')
        actual_at_date = datetime.strftime(actual_at, '%d.%m.%Y')
        actual_at_time = datetime.strftime(actual_at, '%H:%M:%S')

        response_currency = requests.post('https://bbr.ru/graphql/',
                                          cookies=cookies,
                                          headers=headers,
                                          json=json_currency)

        response_json = response_currency.json()
        # Gold string
        internet_bank_exchange = {
            item['fromCurrency']['code']: item for item in response_json['data']['rates']['elements']
        }
        CNY_buy = internet_bank_exchange['CNY']['buyRate']
        CNY_sell = internet_bank_exchange['CNY']['sellRate']

        # add values to dict
        CNY_exchange_rates['CNY'] = {'date': actual_at_date,
                                     'time': actual_at_time,
                                     'buy': CNY_buy,
                                     'sell': CNY_sell
                                     }
        return CNY_exchange_rates

    except Exception:
        url = 'https://wb.bbr.ru/web_banking/protected/refs/currency_rates_of_exchange.jsf'

        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        req = session.get(url)
        # class ="ratesItem ratesItem-positive" > 11.61 < / span >
        CNYRUB_BUY = float(BeautifulSoup(req.text, 'xml').find(class_='currencyRates__wrapper').find(
            class_='ratesItem ratesItem-positive').text)

        CNYRUB_SELL = float(BeautifulSoup(req.text, 'xml').find(class_='currencyRates__wrapper').find(
            class_='ratesItem ratesItem-negative').text)

        CNY_exchange_rates['CNY'] = {'date': '---',
                              'time': '---',
                              'buy': CNYRUB_BUY,
                              'sell': CNYRUB_SELL
                              }

        return CNY_exchange_rates