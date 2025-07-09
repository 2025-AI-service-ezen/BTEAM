from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_connection

bp = Blueprint('users_profile_bp', __name__)

# ✅ DB에서 userid로 사용자 정보를 딕셔너리로 반환하는 함수
def load_user_from_db(userid):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT userid, password, name, phone, birthdate, email FROM users WHERE userid = %s"
    cursor.execute(sql, (userid,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        keys = ['userid', 'password', 'name', 'phone', 'birthdate', 'email']
        return dict(zip(keys, row))
    return None

@bp.route('/profile')
def profile():
    if 'user' not in session:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('users_login_bp.login'))

    user_info = load_user_from_db(session['user'])
    if not user_info:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('users_login_bp.login'))

    # 전화번호 포맷
    phone = user_info.get('phone', '')
    if len(phone) == 11:
        user_info['phone'] = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    elif len(phone) == 10:
        user_info['phone'] = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

    return render_template('profile.html', user=user_info)
