from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('autocomplete_bp', __name__)

@bp.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '').lower()

    stock_list = current_app.config['stock_list']
    suggestions = [name for name in stock_list if query in name.lower()]

    return jsonify(suggestions[:10])
