
from flask import Blueprint, render_template, request, current_app
from app.services.ai.analyzer import predict_price_movement
import os

bp = Blueprint('ai_report_bp', __name__, url_prefix='/report')

@bp.route('/ai', methods=['GET'])
def ai_report():
    stock_name = request.args.get('stock_name', default=None, type=str)
    prediction_result = None

    if stock_name:
        total_df = current_app.config.get('TOTAL_DF', None)
        if total_df is not None and not total_df.empty:
            stock_data = total_df[total_df['종목명'] == stock_name].iloc[-1]
            
            news_text = stock_data['tokens']
            previous_day_change = stock_data['전일비']
            volume = stock_data['거래량']
            
            model_path = os.path.join(current_app.root_path, 'models', 'stock_prediction_model.pkl')

            try:
                prediction_result = predict_price_movement(news_text, previous_day_change, volume, model_path)
            except FileNotFoundError:
                prediction_result = {'error': '모델 파일을 찾을 수 없습니다.'}
            except Exception as e:
                prediction_result = {'error': f'예측 중 오류 발생: {e}'}

    return render_template('AI_report.html', stock_name=stock_name, prediction=prediction_result)

