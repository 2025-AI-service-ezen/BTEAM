from flask import Blueprint, render_template, current_app, json
import pandas as pd

bp = Blueprint('top_chart_bp', __name__)

@bp.route('/top_volume_chart')
def top_volume_chart():
    total_df = current_app.config.get('TOTAL_STOCK_DF', pd.DataFrame())

    if total_df.empty or '종목명' not in total_df.columns or '거래량' not in total_df.columns:
        chart_data = []
    else:
        max_volume_df = total_df.groupby('종목명', as_index=False)['거래량'].max()
        sorted_df = max_volume_df.sort_values(by='거래량', ascending=False)
        top_10_df = sorted_df.head(10)

        chart_data = top_10_df.to_dict(orient='records')
    
    return render_template('top_volume_chart.html', chart_data=json.dumps(chart_data, ensure_ascii=False))
