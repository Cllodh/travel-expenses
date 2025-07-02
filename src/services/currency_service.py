# src/services/currency_service.py
# 匯率查詢與換算服務

import requests

class CurrencyService:
    def __init__(self, base_currency='TWD'):
        self.base_currency = base_currency
        self.api_url = f'https://api.exchangerate-api.com/v4/latest/{self.base_currency}'
        self.rates = self._fetch_rates()

    def _fetch_rates(self):
        try:
            response = requests.get(self.api_url)
            data = response.json()
            return data.get('rates', {})
        except Exception as e:
            print(f'取得匯率失敗: {e}')
            return {}

    def to_twd(self, amount, currency):
        """
        將任意幣別金額換算成台幣
        :param amount: float
        :param currency: str
        :return: float
        """
        if currency == self.base_currency:
            return amount
        rate = self.rates.get(currency)
        if rate:
            return amount / rate
        else:
            print(f'找不到 {currency} 匯率，回傳原金額')
            return amount 