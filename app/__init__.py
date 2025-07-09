import os
import pandas as pd
from flask import Flask, json

from .services.stock.data_loader import load_stock_data_from_db

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    app.config.from_pyfile('config.py')
    app.config['SECRET_KEY'] = 'your_super_secret_key_12345'

    # 경로 설정
    APP_ROOT = app.root_path 
    # app.config['USERS_FILE'] = os.path.join(APP_ROOT, 'users.csv')
    app.config['FAVORITES_FILE'] = os.path.join(APP_ROOT, 'favorites.csv')
    # app.config['FINANCE_DATA_DIR'] = os.path.join(project_root, 'data', 'finance')

    with app.app_context():
        print("데이터 로딩 시작")
        
        # DB에서 직접 데이터 로딩
        stock_list, total_df = load_stock_data_from_db()

        app.logger.info(f"로드된 종목 수: {len(stock_list)}")
        app.logger.info(f"total_df 건수: {len(total_df)}")
        app.logger.info(f"종목명 리스트: {total_df['종목명'].unique()}")
        app.logger.info(f"고유 종목 수: {len(total_df['종목명'].unique())}")

        # 전체 데이터, 종목 리스트 저장
        app.config['STOCK_LIST'] = stock_list # 종목 리스트
        app.config['TOTAL_DF'] = total_df # 전처리된 전체 데이터
       
        # 거래량 기준 상위 종목 정리
        if not total_df.empty and '종목명' in total_df.columns and '거래량' in total_df.columns:
            max_volume_df = total_df.groupby('종목명', as_index=False)['거래량'].max()
            sorted_df = max_volume_df.sort_values(by='거래량', ascending=False)
            app.config['TOP_VOLUME_DF'] = sorted_df
            app.logger.info(f"총 {len(total_df)}건의 주식 데이터 및 거래량 순위 로드 완료.")
        else:
            app.config['TOP_VOLUME_DF'] = pd.DataFrame(columns=['종목명', '거래량'])
            app.logger.warning("거래량 데이터를 로드할 수 없습니다.")

    # Jinja 필터 등록
    def json_load_filter(json_string):
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return []
    app.jinja_env.filters['from_json'] = json_load_filter

    # 라우트 블루프린트 등록
    from .routes.web import index, popup_chart, search, autocomplete
    app.register_blueprint(index.bp)
    app.register_blueprint(popup_chart.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(autocomplete.bp)

    from .routes.users import admin, login, logout, modify, prefer_stock, profile, signup, signout
    app.register_blueprint(admin.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(logout.bp)
    app.register_blueprint(modify.bp)
    app.register_blueprint(prefer_stock.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(signup.bp)
    app.register_blueprint(signout.bp)

    from .routes.stocks import stock_detail
    app.register_blueprint(stock_detail.bp)

    from .routes.volume import top_chart
    app.register_blueprint(top_chart.bp)

    from .routes.api import stocks as api_stocks_bp_module
    from .routes.api import search_api, stock_analysis
    from .routes.report import ai_report
    app.register_blueprint(api_stocks_bp_module.bp, url_prefix='/api')
    app.register_blueprint(search_api.bp, url_prefix='/api')
    app.register_blueprint(stock_analysis.bp, url_prefix='/api')
    app.register_blueprint(ai_report.bp)
    

    return app
