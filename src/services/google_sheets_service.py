# src/services/google_sheets_service.py
# 封裝 Google Sheets 連線與寫入功能

import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEETS_ID, CLIENT_SECRET_FILE, SCOPES

class GoogleSheetsService:
    def __init__(self):
        self.creds = Credentials.from_service_account_file(CLIENT_SECRET_FILE, scopes=SCOPES)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(GOOGLE_SHEETS_ID).sheet1

    def append_row(self, row_data):
        """
        新增一列資料到 Google Sheets。
        :param row_data: List[str]，每個欄位的值
        """
        self.sheet.append_row(row_data, value_input_option='USER_ENTERED') 