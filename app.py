# app.py
# Flask 主入口

from flask import Flask, render_template
from src.components.expense_form import expense_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 請改為安全的隨機字串

# 註冊藍圖
app.register_blueprint(expense_bp)

# 加入靜態頁面路由
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('Terms.html')
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 
