import json
import pandas as pd
from flask import Blueprint, request, render_template, current_app, session, jsonify

from app.services.stock import data_loader 

bp = Blueprint('stocks_search_bp', __name__)

@bp.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('search') or request.form.get('search') or ''
    query = query.strip()
    
    total_df = current_app.config.get('TOTAL_DF')
    if total_df is None:
        current_app.logger.error("TOTAL_DF가 로드되지 않았습니다. 애플리케이션 초기화 시 TOTAL_DF를 로드해야 합니다.")
        return render_template(
            'search.html', 
            user=session.get('user'), 
            search_query=query, 
            stock_list=[], 
            price_chart_data_json='[]',
            error_message="데이터 로드에 문제가 발생했습니다. 관리자에게 문의하세요."
        )

    # 템플릿으로 전달할 변수 초기화
    price_chart_data = []
    stock_name_for_chart = ""
    related_stocks = []
    error_message = None
    search_result_name = None

    if query:
        session['last_search'] = query 

        # 쿼리를 소문자로 변환하여 data_loader와 일관성 유지
        search_query_lower = query.lower()
        
        # total_df에서 정확히 일치하는 종목이 있는지 먼저 확인
        # data_loader.analyze_stock_data에 전달할 DataFrame 내 실제 종목명을 찾습니다.
        # 정확히 일치하는 종목 찾기
        exact_match_df_rows = total_df[total_df['종목명'].str.lower() == search_query_lower]

        if not exact_match_df_rows.empty:
            found_stock_name = exact_match_df_rows['종목명'].iloc[0]  # 원본 종목명 (소문자 변환 X)
            search_result_name = found_stock_name
            stock_name_for_chart = found_stock_name

            # 원본 종목명을 그대로 넣어줌
            analysis_results = data_loader.analyze_stock_data(total_df, found_stock_name)
           
            # ***** 여기를 집중적으로 확인해야 합니다! *****
            if analysis_results and analysis_results.get('price_data'):
                price_chart_data = analysis_results['price_data']


                current_app.logger.debug(f"[{found_stock_name}] data_loader에서 가져온 price_data: {price_chart_data}") # ✅ 이 줄 추가


                if not price_chart_data: # ✅ 데이터가 비어있는지 명확히 확인
                    current_app.logger.warning(f"[{found_stock_name}] 주가 데이터가 비어 있습니다.")
            else:
                current_app.logger.warning(f"'{found_stock_name}'에 대한 유효한 주가 데이터를 찾을 수 없거나 price_data 키가 없습니다.")
                error_message = f'"{query}" 종목의 주가 데이터를 찾을 수 없습니다.'


            # 연관 종목 필터링 (기존 로직 유지)
            all_unique_stocks = total_df['종목명'].dropna().unique().tolist()
            related_stocks = [
                name for name in all_unique_stocks 
                if search_query_lower in name.lower() and name.lower() != search_query_lower
            ]
            related_stocks = related_stocks[:5] # 상위 5개 연관 종목만 반환

        else: # 쿼리와 정확히 일치하는 종목을 찾지 못한 경우
            error_message = f'"{query}"에 해당하는 종목을 찾을 수 없습니다.'
            
            # 부분 일치하는 모든 종목을 연관 종목으로 표시
            all_unique_stocks = total_df['종목명'].dropna().unique().tolist()
            related_stocks = [name for name in all_unique_stocks if query.lower() in name.lower()]
            related_stocks = related_stocks[:10] # 상위 10개 부분 일치 종목 반환

    price_chart_data_json = json.dumps(price_chart_data, ensure_ascii=False)


    current_app.logger.debug(f"Flask에서 템플릿으로 전송될 최종 price_chart_data_json: {price_chart_data_json}")


    return render_template(
        'search.html',
        user=session.get('user'),
        search_query=query,
        price_chart_data_json=price_chart_data_json,
        stock_name_for_chart=stock_name_for_chart,
        related_stocks=related_stocks,
        error_message=error_message,
        search_result_name=search_result_name
    )

@bp.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '').strip().lower()
    total_df = current_app.config.get('TOTAL_DF')

    if total_df is None or not query:
        return jsonify([])

    all_names = total_df['종목명'].dropna().unique().tolist()
    matches = [name for name in all_names if query in name.lower()]
    return jsonify(matches[:10]) 


# 뉴스 데이터 API 엔드포인트
@bp.route('/api/news')
def api_news():
    company_name = request.args.get('company_name', '').strip()
    if not company_name:
        return jsonify({'error': '종목명이 필요합니다.'}), 400

    total_df = current_app.config.get('TOTAL_DF')
    if total_df is None:
        current_app.logger.error("TOTAL_DF가 로드되지 않았습니다.")
        return jsonify({'error': '뉴스 데이터를 불러올 수 없습니다. 관리자에게 문의하세요.'}), 500

    try:
        company_name_lower = company_name.lower()
        matched_rows = total_df[total_df['종목명'].str.lower() == company_name_lower]

        if matched_rows.empty:
            current_app.logger.warning(f"뉴스 대상 종목을 찾을 수 없습니다: '{company_name}'")
            return jsonify({'news_articles': [], 'message': f"'{company_name}'에 대한 뉴스 기사를 찾을 수 없습니다."}), 200

        actual_stock_name = matched_rows['종목명'].iloc[0].lower()
        analysis_results = data_loader.analyze_stock_data(total_df, actual_stock_name)
        
        news_articles = analysis_results.get('news_articles', [])

        if not news_articles:
            return jsonify({'news_articles': [], 'message': f"'{actual_stock_name}'에 대한 뉴스 기사를 찾을 수 없습니다."}), 200

        return jsonify({'news_articles': news_articles})

    except Exception as e:
        current_app.logger.error(f"뉴스 데이터 가져오는 중 오류: {e}")
        return jsonify({'error': '뉴스 데이터를 가져오는 중 오류가 발생했습니다.'}), 500