from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import json

# API를 위한 블루프린트 이름
bp = Blueprint('api_stocks_bp', __name__)

# 이 라우트는 __init__.py에서 url_prefix='/api'로 설정되므로,
# 여기서는 라우트 경로를 '/'로 시작합니다.
@bp.route('/stocks', methods=['GET'])
def get_stocks_api(): # main_pg의 index() 또는 다른 get_stocks와 충돌을 피하기 위해 함수 이름 변경
    TOP_VOLUME_DF = current_app.config.get('TOP_VOLUME_DF', pd.DataFrame(columns=['company', '거래량']))

    limit = request.args.get('limit', 5, type=int)
    offset = request.args.get('offset', 0, type=int)
    api_search_query = request.args.get('search', '').strip()

    filtered_df = TOP_VOLUME_DF

    if api_search_query:
        if 'company' in TOP_VOLUME_DF.columns:
            filtered_df = TOP_VOLUME_DF[TOP_VOLUME_DF['company'].str.contains(api_search_query, case=False, na=False)]
        else:
            filtered_df = pd.DataFrame(columns=['company', '거래량'])

    total_filtered_stocks = len(filtered_df)
    stocks_to_send = filtered_df.iloc[offset : offset + limit].to_dict(orient='records')

    return jsonify({
        'stocks': stocks_to_send,
        'has_more': (offset + limit) < total_filtered_stocks,
        'total': total_filtered_stocks
    })