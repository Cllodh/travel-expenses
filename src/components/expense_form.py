# src/components/expense_form.py
# 旅行花費表單頁面與提交

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from src.services.currency_service import CurrencyService
import requests

expense_bp = Blueprint('expense', __name__)

currency_service = CurrencyService()

COUNTRY_CURRENCY = {
    '日本': 'JPY',
    '韓國': 'KRW',
    '美國': 'USD',
    '泰國': 'THB',
    '法國': 'EUR',
    '德國': 'EUR',
    '英國': 'GBP',
    '澳洲': 'AUD',
    '越南': 'VND',
    '馬來西亞': 'MYR',
    '香港': 'HKD',
    '義大利': 'EUR',
    '新加坡': 'SGD',
    '印尼': 'IDR',
    '菲律賓': 'PHP',
    '加拿大': 'CAD',
    '紐西蘭': 'NZD'
}

def parse_multi_currency(text):
    """
    將如 '100, 200' 轉為 [100, 200]
    """
    result = []
    if not text:
        return result
    for part in text.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(float(part))
        except ValueError:
            continue
    return result

def add_currency_symbol(amounts, symbol):
    return ', '.join([f"{symbol} {a}" for a in amounts]) if amounts else ''

@expense_bp.route('/', methods=['GET', 'POST'])
def expense_form():
    if request.method == 'POST':
        print('收到表單資料:', dict(request.form))
        # 取得表單資料
        country = request.form.get('country')
        period = request.form.get('period')
        days = request.form.get('days')
        ticket = float(request.form.get('ticket') or 0)
        hotel = float(request.form.get('hotel') or 0)
        sim = float(request.form.get('sim') or 0)
        klook = float(request.form.get('klook') or 0)
        exchange = request.form.get('exchange')
        card = request.form.get('card')
        original_currency = request.form.get('original_currency')
        balance = request.form.get('balance')
        insurance = float(request.form.get('insurance') or 0)
        currency = COUNTRY_CURRENCY.get(country, '') if country != '其他' else ''
        exchange_list = parse_multi_currency(exchange)
        card_list = parse_multi_currency(card)
        original_list = parse_multi_currency(original_currency)
        balance_list = parse_multi_currency(balance)
        exchange_str = add_currency_symbol(exchange_list, 'TWD')
        card_str = add_currency_symbol(card_list, currency)
        original_str = add_currency_symbol(original_list, currency)
        balance_str = add_currency_symbol(balance_list, currency)
        # 換匯直接加總（台幣）
        exchange_twd = sum(exchange_list)
        # 其他三個欄位用匯率換算成台幣
        rate = float(request.form.get('rate') or 0)
        if rate <= 0:
            flash('匯率必須大於0，請正確填寫！')
            return redirect(url_for('expense.expense_form'))
        def to_twd_local(amount):
            try:
                return float(amount) / rate if rate else 0
            except Exception:
                return 0
        card_twd = sum([to_twd_local(amount) for amount in card_list])
        original_twd = sum([to_twd_local(amount) for amount in original_list])
        balance_twd = sum([to_twd_local(amount) for amount in balance_list])
        # 先合併 (換匯 + 原本有的貨幣 - 現餘)
        other_twd = exchange_twd + original_twd - balance_twd
        # 計算總花費
        total = ticket + hotel + insurance + sim + klook + card_twd + other_twd
        total = round(total, 2)
        spreadsheet_id = request.form.get('spreadsheet_id')
        access_token = request.form.get('google_access_token')
        print('spreadsheet_id:', spreadsheet_id)
        print('access_token:', access_token)
        row = [country, period, days, ticket, hotel, sim, klook, insurance, exchange_str, card_str, original_str, balance_str, rate, total]
        if access_token and spreadsheet_id:
            # 先檢查 spreadsheet 是否存在
            check_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}'
            check_headers = {'Authorization': f'Bearer {access_token}'}
            check_resp = requests.get(check_url, headers=check_headers)
            if check_resp.status_code == 404:
                flash('Google Sheets 檔案不存在，請重新登入或建立新表單！')
                return redirect(url_for('expense.expense_form'))
            # 用 Google Sheets API 幫 user 寫入自己的表單
            url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/工作表1!A1:append?valueInputOption=USER_ENTERED'
            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'values': [row]}
            r = requests.post(url, headers=headers, json=data)
            result = r.json()
            print('Google Sheets API 回應:', result)
            if 'error' in result:
                flash('寫入 Google Sheets 失敗：' + result['error']['message'])
            else:
                flash('已成功寫入您的 Google Sheets！')
        else:
            flash('未登入 Google 或未填寫 Google Sheets ID，僅本地處理（不寫入 Google Sheets）')
        return redirect(url_for('expense.expense_form'))
    return render_template('expense_form.html')

@expense_bp.route('/rate')
def get_rate():
    currency = request.args.get('currency')
    if not currency or currency.upper() == 'TWD':
        return jsonify({'rate': 1})
    rate = currency_service.rates.get(currency.upper())
    if rate:
        return jsonify({'rate': round(1/rate, 4)})
    return jsonify({'rate': None}) 