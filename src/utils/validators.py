# src/utils/validators.py
# 表單輸入驗證工具

def is_positive_number(value):
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False 