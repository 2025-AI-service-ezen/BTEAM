# stock_recommender/app/routes/users/admin.py

from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('users_admin_bp', __name__)

@bp.route('/admin')
def admin():
    if 'user' not in session: # 관리자만 접근 가능하도록 추가 로직 필요
        return redirect(url_for('users_login_bp.login'))
    # 관리자 특정 로직을 여기에 추가합니다.
    return render_template('admin.html') # 이 템플릿을 생성해야 할 수 있습니다.