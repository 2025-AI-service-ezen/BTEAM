from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection  # ✅ MySQL 연결용 추가

bp = Blueprint('users_signup_bp', __name__)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        birthdate = request.form['birthdate'].strip()
        email = request.form['email'].strip()

        # 입력 유효성 검사
        if not all([userid, password, name, phone, birthdate, email]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('signup.html')

        if len(userid) < 4 or len(userid) > 20:
            flash('아이디는 4자 이상 20자 이하여야 합니다.', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('비밀번호는 최소 6자 이상이어야 합니다.', 'error')
            return render_template('signup.html')

        if len(birthdate) == 8 and birthdate.isdigit():
            birthdate_formatted = f"{birthdate[:4]}-{birthdate[4:6]}-{birthdate[6:]}"
        else:
            flash('생년월일 형식이 올바르지 않습니다 (YYYYMMDD 형식으로 8자리 숫자).', 'error')
            return render_template('signup.html')

        # ✅ DB 중복 확인 및 저장
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                # 중복 아이디 체크
                sql_check = "SELECT COUNT(*) AS cnt FROM users WHERE userid = %s"
                cursor.execute(sql_check, (userid,))
                result = cursor.fetchone()

                if result['cnt'] > 0:
                    flash('이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.', 'error')
                    return render_template('signup.html')

                # 회원가입 정보 저장
                sql_insert = """
                    INSERT INTO users (userid, password, name, phone, birthdate, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (userid, password, name, phone, birthdate_formatted, email))
                conn.commit()

        except Exception as e:
            flash(f'DB 저장 중 오류 발생: {e}', 'error')
            return render_template('signup.html')
        finally:
            conn.close()

        flash('회원가입이 성공적으로 완료되었습니다. 로그인해주세요!', 'success')
        return redirect(url_for('users_login_bp.login'))

    return render_template('signup.html')
