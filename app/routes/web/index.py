from flask import Blueprint, render_template, session, current_app, json
from db import get_stock_connection  # 주식 데이터 DB 연결 함수
import pandas as pd
import os

bp = Blueprint('web_index_bp', __name__)

@bp.route('/', methods=['GET'])
def index():
    is_login = 'user' in session
    user = session.get('user', '')

    # DB에서 거래량 최대값 기준 Top 5 종목 조회
    try:
        conn = get_stock_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT company_name AS 종목명, MAX(volume) AS 거래량
                FROM stock_news
                GROUP BY company_name
                ORDER BY 거래량 DESC
                LIMIT 5
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

        current_app.logger.info(f"DB에서 조회된 Top5 rows: {rows}")

        if not rows:
            initial_stocks_json = '[]'
            current_app.logger.info("DB에서 조회된 거래량 Top5 데이터가 없습니다.")
        else:
            df = pd.DataFrame(rows)
            current_app.logger.info(f"Top5 DataFrame:\n{df.to_string(index=False)}")
            initial_stocks_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)

    except Exception as e:
        current_app.logger.error(f"거래량 Top5 조회 중 오류 발생: {e}")
        initial_stocks_json = '[]'
    finally:
        conn.close()

    # 선호 주식 관련 데이터 초기화
    stock_display = []
    stock_list_json = '[]'

    if is_login:
        favorites = load_favorites()
        stock_display = get_user_stock_display(favorites)
        # 현재는 빈 리스트, 필요 시 DB에서 전체 종목 리스트 로드 코드 추가 가능
        stock_list_json = '[]'

    return render_template('index.html',
        is_login=is_login,
        user=user,
        initial_stocks_json=initial_stocks_json,
        stock_display=stock_display,
        stock_list_json=stock_list_json
    )


# 기존 CSV 기반 선호주식 로드 함수 (DB 전환 원하면 알려주세요)
def load_favorites():
    favorites_file = current_app.config['FAVORITES_FILE']
    if os.path.exists(favorites_file):
        return pd.read_csv(favorites_file, encoding='utf-8')
    else:
        os.makedirs(os.path.dirname(favorites_file), exist_ok=True)
        return pd.DataFrame(columns=['userid', 'stock_name'])


def get_user_stock_display(favorites):
    user_stocks = favorites[favorites['userid'] == session['user']]
    return [{'name': row['stock_name']} for _, row in user_stocks.iterrows()]
