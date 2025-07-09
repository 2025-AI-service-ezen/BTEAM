from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, json
import pandas as pd
import os

bp = Blueprint('users_prefer_stock_bp', __name__)

# 선호 주식 로딩 헬퍼 함수
def load_favorites():
    favorites_file = current_app.config['FAVORITES_FILE']
    if os.path.exists(favorites_file):
        return pd.read_csv(favorites_file, encoding='utf-8')
    else:
        os.makedirs(os.path.dirname(favorites_file), exist_ok=True)
        return pd.DataFrame(columns=['userid', 'stock_name'])


@bp.route('/prefer_stock', methods=['GET', 'POST'])
def prefer_stock():
    if 'user' not in session:
        return redirect(url_for('users_login_bp.login'))

    favorites = load_favorites()

    # 전처리된 데이터 가져오기
    total_df = current_app.config['TOTAL_DF']

    # 종목명 리스트 생성 (중복 제거)
    stock_list = (
        total_df[['종목명']]
        .drop_duplicates()
        .rename(columns={'종목명': 'stock_name'})
        .to_dict(orient='records')
    )

    if request.method == 'POST':
        stock_input = request.form['stock_input'].strip()

        # 종목명으로만 검색
        matched_stock = next(
            (s for s in stock_list if s['stock_name'] == stock_input),
            None
        )

        if not matched_stock:
            return render_template('prefer_stock.html',
                                   error="해당 종목을 찾을 수 없습니다.",
                                   stock_display=get_user_stock_display(favorites),
                                   stock_list_json=json.dumps(stock_list, ensure_ascii=False))

        stock_name = matched_stock['stock_name']

        # 중복 여부 확인
        is_duplicate = ((favorites['userid'] == session['user']) &
                        (favorites['stock_name'] == stock_name)).any()

        if not is_duplicate:
            new_fav = pd.DataFrame([{
                'userid': session['user'],
                'stock_name': stock_name
            }])
            favorites = pd.concat([favorites, new_fav], ignore_index=True)
            favorites.to_csv(current_app.config['FAVORITES_FILE'], index=False, encoding='utf-8')

        return redirect(url_for('web_index_bp.index'))

    # 기존 선호 주식 표시
    stock_display = get_user_stock_display(favorites)

    return render_template('prefer_stock.html',
                           stock_display=stock_display,
                           stock_list_json=json.dumps(stock_list, ensure_ascii=False))


# 선호주식 삭제
@bp.route('/prefer_stock/delete/<stock_name>', methods=['POST'])
def delete_prefer_stock(stock_name):
    if 'user' not in session:
        return redirect(url_for('users_login_bp.login'))

    favorites = load_favorites()

    favorites = favorites[
        ~((favorites['userid'] == session['user']) & (favorites['stock_name'] == stock_name))
    ]

    favorites.to_csv(current_app.config['FAVORITES_FILE'], index=False, encoding='utf-8')

    return redirect(url_for('web_index_bp.index'))


# 추천 검색어 기능
@bp.route('/prefer_stock/suggestions')
def stock_suggestions():
    if 'user' not in session:
        return [], 403

    query = request.args.get('q', '').strip()

    total_df = current_app.config['TOTAL_DF']
    suggestions = []

    for _, row in total_df[['종목명']].drop_duplicates().iterrows():
        name = row['종목명']
        if query in name:
            suggestions.append(name)
    # 주식코드가 있을때,
    # for _, row in total_df[['종목명', 'code']].drop_duplicates().iterrows():
    #     name = row['종목명']
    #     code = str(row['code'])
    #     if query in name or query in code:
    #         suggestions.append(f"{name} ({code})")


    return json.dumps(suggestions), 200


# 기존 선호 주식 표시 리스트 반환
def get_user_stock_display(favorites):
    user_stocks = favorites[favorites['userid'] == session['user']]
    return [
        # 주식 코드가 있을 때,
        # {'name': row['stock_name'], 'code': str(row['stock_code'])}
        {'name': row['stock_name']}
        for _, row in user_stocks.iterrows()
    ]

