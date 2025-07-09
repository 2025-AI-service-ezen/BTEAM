from db import get_stock_connection
# stock_news DB 연결함수

import pandas as pd
import json
import sys
import os

# 이 파일이 Flask 앱 컨텍스트 내에서 실행될 때는 current_app.logger를 사용하고,
# 단독으로 실행될 때는 기본 print 함수를 사용하도록 합니다.
def get_logger_or_print():
    try:
        from flask import current_app
        # Flask 앱 컨텍스트 내에 있고 logger가 유효하면 로거 객체 반환
        if current_app and current_app.logger:
            return current_app.logger
        else: # 혹시 current_app은 있어도 logger가 없을 경우 대비 (거의 발생 안 함)
            return print 
    except RuntimeError: # Flask 컨텍스트 밖에서 current_app 접근 시 발생
        return print # 컨텍스트 밖이면 print 함수 반환
    except ImportError: # Flask가 설치되지 않았을 경우 (매우 드물게 발생)
        return print


# 주식 데이터 로딩 함수
def load_stock_data_from_db():
    _logger = get_logger_or_print()

    conn = get_stock_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                company_name AS 종목명,
                stock_code AS 종목코드,
                date AS 날짜,
                close_price AS 종가,
                price_change AS 전일비,
                open_price AS 시가,
                high_price AS 고가,
                low_price AS 저가,
                volume AS 거래량,
                news_title AS 제목,
                url AS 링크
            FROM stock_news
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            if not rows:
                _logger.warning("DB에서 로드할 데이터가 없습니다.")
                return [], pd.DataFrame(columns=['종목명', '종목코드', '날짜', '종가', '전일비', '시가', '고가', '저가', '거래량', '제목', '링크'])

            df = pd.DataFrame(rows)
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
            df.dropna(subset=['날짜'], inplace=True)
            df['종목명'] = df['종목명'].astype(str).str.strip().str.lower()

            stock_list = df['종목명'].unique().tolist()
            _logger.info(f"총 {len(df)}개의 데이터 포인트 로드. 고유 종목 수: {len(stock_list)}")

            return stock_list, df

    except Exception as e:
        _logger.error(f"DB 데이터 로드 중 오류: {e}")
        return [], pd.DataFrame(columns=['종목명', '종목코드', '날짜', '종가', '전일비', '시가', '고가', '저가', '거래량', '제목', '링크'])

    finally:
        conn.close()


# 주식데이터와 뉴스 기사 추출(주식 분석 함수)
def analyze_stock_data(data_df, company_name):
    _logger = get_logger_or_print()
    _logger.debug(f"\n'{company_name}' 종목 정보 추출 중...\n")

    search_company_name = company_name.strip().lower()
    stock_data = data_df[data_df['종목명'] == search_company_name].copy()

    if stock_data.empty:
        _logger.warning(f"'{company_name}'에 대한 데이터를 찾을 수 없습니다.")
        return {}

    stock_data = stock_data.sort_values(by='날짜')
    _logger.info(f"'{company_name}' 종목의 데이터 ({len(stock_data)}개)를 찾았습니다.")

    # 주가 데이터 추출
    stock_data['종가'] = pd.to_numeric(stock_data['종가'], errors='coerce')
    price_data = stock_data[['날짜', '종가']].dropna().to_dict(orient='records')
    for item in price_data:
        item['날짜'] = item['날짜'].strftime('%Y-%m-%d')

    if not price_data:
        _logger.warning(f"'{company_name}' 종목의 유효한 주가 데이터가 없습니다.")

    # 뉴스 데이터 추출
    news_articles = stock_data[['날짜', '제목', '링크']].drop_duplicates(subset=['제목', '링크']).sort_values(by='날짜', ascending=False)
    news_list = []
    if not news_articles.empty:
        for _, row in news_articles.head(10).iterrows():
            news_list.append({
                'date': row['날짜'].strftime('%Y-%m-%d'),
                'title': row['제목'],
                'link': row['링크']
            })
        _logger.info(f"총 {len(news_articles)}개의 기사 중 상위 10개 데이터 준비.")

    return {
        'price_data': price_data,
        'news_articles': news_list
    }


# 메인 실행 블록 (스크립트를 직접 실행할 때만 동작)         # 개인적으로 이부분 가장 많이 이해 않감
if __name__ == "__main__":
    _logger = get_logger_or_print()
    
    _logger.info("DB에서 주식 데이터 로드 시도 중...")
    stock_list, total_df = load_stock_data_from_db()

    if total_df.empty:
        _logger.warning("로딩된 데이터가 없어 분석을 계속할 수 없습니다.")
    else:
        _logger.info("\n--- 로드된 종목 목록 ---")
        for i, stock in enumerate(stock_list):
            _logger.info(f"{i+1}. {stock}")
        _logger.info("----------------------")

        input_company = input("검색할 주식 종목명을 입력하세요: ")

        analysis_results = analyze_stock_data(total_df, input_company)

        if analysis_results:
            _logger.debug("\n--- 주가 데이터 (JSON) ---")
            _logger.debug(json.dumps(analysis_results.get('price_data', []), indent=2, ensure_ascii=False))

            _logger.debug("\n--- 뉴스 기사 데이터 ---")
            _logger.debug(json.dumps(analysis_results.get('news_articles', []), indent=2, ensure_ascii=False))

            _logger.info("\n이 데이터는 이제 웹 프런트엔드로 전달해 시각화할 수 있습니다.")
        else:
            _logger.warning("데이터 분석 결과가 없습니다.")
