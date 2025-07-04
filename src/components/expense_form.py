# src/components/expense_form.py
# 旅行花費表單頁面與提交

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from src.services.currency_service import CurrencyService
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

expense_bp = Blueprint('expense', __name__)

currency_service = CurrencyService()

COUNTRY_CURRENCY = {
    '台灣': 'TWD',
    '澳門': 'MOP',
    '香港': 'HKD',
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
    '義大利': 'EUR',
    '新加坡': 'SGD',
    '印尼': 'IDR',
    '菲律賓': 'PHP',
    '加拿大': 'CAD',
    '紐西蘭': 'NZD',
    '中國': 'CNY'
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

class ExpenseForm(FlaskForm):
    country = StringField('國家', validators=[DataRequired()])
    period = StringField('時間區間', validators=[DataRequired()])
    days = IntegerField('天數', validators=[DataRequired(), NumberRange(min=1, message='天數需大於0')])
    ticket = FloatField('機票', validators=[NumberRange(min=0)], default=0)
    hotel = FloatField('住宿', validators=[NumberRange(min=0)], default=0)
    sim = FloatField('SIM', validators=[NumberRange(min=0)], default=0)
    klook = FloatField('票券', validators=[NumberRange(min=0)], default=0)
    insurance = FloatField('保險', validators=[NumberRange(min=0)], default=0)
    exchange = StringField('換匯', validators=[Optional()])
    card = StringField('刷卡', validators=[Optional()])
    original_currency = StringField('原本有的貨幣', validators=[Optional()])
    balance = StringField('現餘', validators=[Optional()])
    rate = FloatField('匯率', validators=[DataRequired(), NumberRange(min=0.0001, message='匯率必須大於0')])
    spreadsheet_id = StringField('spreadsheet_id', validators=[Optional()])
    google_access_token = StringField('google_access_token', validators=[Optional()])
    submit = SubmitField('送出')

@expense_bp.route('/', methods=['GET', 'POST'])
def expense_form():
    form = ExpenseForm()
    if form.validate_on_submit():
        # 取得表單資料
        country = form.country.data
        period = form.period.data
        days = form.days.data
        ticket = form.ticket.data or 0
        hotel = form.hotel.data or 0
        sim = form.sim.data or 0
        klook = form.klook.data or 0
        exchange = form.exchange.data
        card = form.card.data
        original_currency = form.original_currency.data
        balance = form.balance.data
        insurance = form.insurance.data or 0
        currency = COUNTRY_CURRENCY.get(country, '') if country != '其他' else ''
        exchange_list = parse_multi_currency(exchange)
        card_list = parse_multi_currency(card)
        original_list = parse_multi_currency(original_currency)
        balance_list = parse_multi_currency(balance)
        exchange_str = add_currency_symbol(exchange_list, 'TWD')
        card_str = add_currency_symbol(card_list, currency)
        card_str = card_str.replace('TWD', currency)
        original_str = add_currency_symbol(original_list, currency)
        balance_str = add_currency_symbol(balance_list, currency)
        exchange_twd = sum(exchange_list)
        rate = form.rate.data
        def to_twd_local(amount):
            try:
                return float(amount) / rate if rate else 0
            except Exception:
                return 0
        card_twd = sum([to_twd_local(amount) for amount in card_list])
        original_twd = sum([to_twd_local(amount) for amount in original_list])
        balance_twd = sum([to_twd_local(amount) for amount in balance_list])
        other_twd = exchange_twd + original_twd - balance_twd
        total = ticket + hotel + insurance + sim + klook + card_twd + other_twd
        total = round(total, 2)
        spreadsheet_id = form.spreadsheet_id.data
        access_token = form.google_access_token.data
        row = [country, period, days, ticket, hotel, sim, klook, insurance, exchange_str, card_str, original_str, balance_str, rate, total]
        if access_token and spreadsheet_id:
            check_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}'
            check_headers = {'Authorization': f'Bearer {access_token}'}
            check_resp = requests.get(check_url, headers=check_headers)
            if check_resp.status_code == 404:
                flash('Google Sheets 檔案不存在，請重新登入或建立新表單！')
                return redirect(url_for('expense.expense_form'))
            headers = [
                '旅行國家', '時間區間', '天數', '機票', '住宿', 'SIM', '票券', '保險',
                '換匯', '刷卡', '原本有的貨幣', '現餘', '匯率', '總花費'
            ]
            update_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/工作表1!A1:N1?valueInputOption=USER_ENTERED'
            update_data = {'values': [headers]}
            requests.put(update_url, headers=check_headers, json=update_data)
            url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/工作表1!A1:append?valueInputOption=USER_ENTERED'
            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'values': [row]}
            r = requests.post(url, headers=headers, json=data)
            result = r.json()
            if 'error' in result:
                flash('寫入 Google Sheets 失敗：' + result['error']['message'])
            else:
                flash('已成功寫入您的 Google Sheets！')
        else:
            flash('未登入 Google 或未填寫 Google Sheets ID，僅本地處理（不寫入 Google Sheets）')
        return redirect(url_for('expense.expense_form'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}：{error}")
    return render_template('expense_form.html', form=form)

@expense_bp.route('/rate')
def get_rate():
    currency = request.args.get('currency')
    if not currency or currency.upper() == 'TWD':
        return jsonify({'rate': 1})
    rate = currency_service.rates.get(currency.upper())
    if rate:
        return jsonify({'rate': round(1/rate, 4)})
    return jsonify({'rate': None})

@expense_bp.route('/api/countries')
def get_countries():
    return jsonify(COUNTRY_CURRENCY) 