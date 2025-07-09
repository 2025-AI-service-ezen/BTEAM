from flask import Blueprint, render_template, session, redirect, url_for, current_app
import pandas as pd

bp = Blueprint('stocks_detail_bp', __name__)

@bp.route('/stock/<stock_name>')
def stock_detail(stock_name):
    if 'user' not in session:
        return redirect(url_for('users_login_bp.login'))

    TOTAL_STOCK_DF = current_app.config.get('TOTAL_STOCK_DF', pd.DataFrame())

    stock_data = TOTAL_STOCK_DF[TOTAL_STOCK_DF['종목명'] == stock_name]

    if stock_data.empty:
        return "주식을 찾을 수 없습니다.", 404

    # 템플릿에 주식 데이터 전달
    # Jinja 렌더링을 위해 DataFrame을 사전으로 변환
    stock_info = stock_data.to_dict(orient='records')
    return render_template('stock_detail.html', stock_info=stock_info, stock_name=stock_name)