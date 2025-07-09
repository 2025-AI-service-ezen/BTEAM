from flask import Blueprint, request, jsonify, current_app
from app.services.stock.data_loader import analyze_stock_data # app 패키지에서 절대 경로 임포트

bp = Blueprint('api_stock_analysis', __name__, url_prefix='/api')

@bp.route('/analyze', methods=['GET'])
def get_stock_analysis():
    """
    쿼리 파라미터로 받은 종목명에 대해 주가 데이터와 뉴스 기사를 JSON 형태로 반환합니다.
    예상 URL: /api/analyze?company_name=삼성전자
    """
    company_name = request.args.get('company_name')

    if not company_name:
        return jsonify({'error': '종목명(company_name) 파라미터가 필요합니다.'}), 400

    total_df = current_app.config.get('TOTAL_DF')

    if total_df is None or total_df.empty:
        return jsonify({'error': '서버에 주식 데이터가 로드되지 않았습니다.'}), 500

    # 분석 함수를 호출하여 구조화된 데이터 가져오기
    analysis_results = analyze_stock_data(total_df, company_name)

    if not analysis_results:
        return jsonify({'error': f"'{company_name}'에 대한 데이터를 찾을 수 없습니다. 정확한 종목명을 확인해주세요."}), 404
    
    # 결과를 JSON으로 반환
    return jsonify(analysis_results), 200