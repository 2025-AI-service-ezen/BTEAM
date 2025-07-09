from flask import Blueprint, render_template, current_app, json
import pandas as pd
from db import get_connection

bp = Blueprint('popup_chart_bp', __name__)

@bp.route('/popup_chart')
def popup_chart():
    total_df = current_app.config.get('TOTAL_DF', pd.DataFrame())

    if total_df.empty or '종목명' not in total_df.columns or '거래량' not in total_df.columns:
        sorted_df = pd.DataFrame(columns=['종목명', '거래량'])
    else:
        max_volume_df = total_df.groupby('종목명', as_index=False)['거래량'].max()
        sorted_df = max_volume_df.sort_values(by='거래량', ascending=False)

    top20_df = sorted_df.head(20)
    chart_data = top20_df.to_dict(orient='records')

    return render_template('popup_chart.html', chart_data=json.dumps(chart_data, ensure_ascii=False))
