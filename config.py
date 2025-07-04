# config.py
# 專案設定檔，集中管理所有配置

import os

GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID')
CLIENT_SECRET_FILE = os.environ.get('CLIENT_SECRET_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DEFAULT_CURRENCY = 'TWD' 