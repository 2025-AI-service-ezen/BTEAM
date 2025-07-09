from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_connection

bp = Blueprint('users_login_bp', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()

        print('로그인 입력값:', repr(userid), repr(password))

        if not userid or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html')

        user = None
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()  # dictionary=True 제거!
            sql = "SELECT * FROM users WHERE userid = %s AND password = %s"
            cursor.execute(sql, (userid, password))
            user = cursor.fetchone()
            print('DB select 결과:', user)  # 튜플로 출력됨
            cursor.close()
        except Exception as e:
            print('DB 에러:', e)
            flash(f'데이터베이스 연결/조회 중 오류가 발생했습니다: {e}', 'error')
            return render_template('login.html')
        finally:
            if conn:
                conn.close()

        if user:
            session.permanent = False
            session['user'] = userid
            flash('로그인 성공!', 'success')
            return redirect(url_for('web_index_bp.index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
            return render_template('login.html')

    return render_template('login.html')
