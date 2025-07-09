from flask import Blueprint, session, redirect, url_for

bp = Blueprint('users_logout_bp', __name__)

@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('web_index_bp.index')) # 초기 메인 페이지로 리다이렉트