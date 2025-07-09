from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('search_api_bp', __name__)

@bp.route('/search_stocks', methods=['GET'])
def search_stocks():
    query = request.args.get('query', '').strip().lower()

    if not query:
        return jsonify([])

    # 후에 주식코드가 있따면 [('삼성전자', '005930'), ('현대차', '005380'), ...] 이런 형태로
    stock_list = current_app.config.get('STOCK_LIST')

    # query가 이름 또는 코드에 포함되는 항목만 필터
    results = [
        {'name': name}
        for name in stock_list
        # if query in name.lower() or query in code.lower()
        if query in name.lower()
    ]

    return jsonify(results[:50])
