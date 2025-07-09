# stock_recommender/app/routes/stocks/stock_unrec.py

from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('stocks_unrec_bp', __name__)

@bp.route('/unrecommended_stocks')
def unrecommended_stocks():
    if 'user' not in session:
        return redirect(url_for('users_login_bp.login'))
    # 주식 비추천을 위한 로직
    return render_template('unrecommended_stocks.html') # 이 템플릿을 생성하세요.