from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_connection

bp = Blueprint('users_modify_bp', __name__)

# ✅ DB에서 userid로 사용자 정보 가져오는 함수
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

@bp.route('/modify', methods=['GET', 'POST'])
def modify():
    if 'user' not in session:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('users_login_bp.login'))

    current_userid = session['user']
    user_info = load_user_from_db(current_userid)
    if not user_info:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('users_login_bp.login'))

    if request.method == 'POST':
        new_name = request.form['name'].strip()
        new_phone = request.form['phone'].strip()
        new_birthdate = request.form['birthdate'].strip()
        new_email = request.form['email'].strip()

        if not all([new_name, new_phone, new_birthdate, new_email]):
            flash('이름, 전화번호, 생년월일, 이메일은 필수 입력 사항입니다.', 'error')
            user_info.update({'name': new_name, 'phone': new_phone, 'birthdate': new_birthdate, 'email': new_email})
            return render_template('modify.html', user=user_info)

        if len(new_birthdate) == 8 and new_birthdate.isdigit():
            new_birthdate_formatted = f"{new_birthdate[:4]}-{new_birthdate[4:6]}-{new_birthdate[6:]}"
        else:
            flash('생년월일 형식이 올바르지 않습니다 (YYYYMMDD 형식으로 8자리 숫자).', 'error')
            user_info.update({'name': new_name, 'phone': new_phone, 'birthdate': new_birthdate, 'email': new_email})
            return render_template('modify.html', user=user_info)

        # 비밀번호 변경 관련
        current_password_input = request.form.get('current_password', '').strip()
        new_password_input = request.form.get('new_password', '').strip()
        confirm_password_input = request.form.get('confirm_password', '').strip()

        password_changed = False

        # 비밀번호 변경 로직
        if new_password_input:
            if not current_password_input:
                flash('새 비밀번호를 설정하려면 현재 비밀번호를 입력해야 합니다.', 'error')
                user_info.update({'name': new_name, 'phone': new_phone, 'birthdate': new_birthdate, 'email': new_email})
                return render_template('modify.html', user=user_info)

            if user_info['password'] != current_password_input:
                flash('현재 비밀번호가 일치하지 않습니다.', 'error')
                user_info.update({'name': new_name, 'phone': new_phone, 'birthdate': new_birthdate, 'email': new_email})
                return render_template('modify.html', user=user_info)

            if new_password_input != confirm_password_input:
                flash('새 비밀번호와 확인 비밀번호가 일치하지 않습니다.', 'error')
                user_info.update({'name': new_name, 'phone': new_phone, 'birthdate': new_birthdate, 'email': new_email})
                return render_template('modify.html', user=user_info)

            if len(new_password_input) < 6:
                flash('새 비밀번호는 최소 6자 이상이어야 합니다.', 'error')
                user_info.update({'name': new_name, 'phone': new_phone, 'birthdate': new_birthdate, 'email': new_email})
                return render_template('modify.html', user=user_info)

            # ✅ DB에 비밀번호 포함 UPDATE
            try:
                conn = get_connection()
                cursor = conn.cursor()
                sql = """
                    UPDATE users
                    SET name=%s, phone=%s, birthdate=%s, email=%s, password=%s
                    WHERE userid=%s
                """
                cursor.execute(sql, (new_name, new_phone, new_birthdate_formatted, new_email, new_password_input, current_userid))
                conn.commit()
                cursor.close()
                conn.close()
                password_changed = True
            except Exception as e:
                flash(f'회원정보 수정 중 오류 발생: {e}', 'error')
                return render_template('modify.html', user=user_info)
        else:
            # ✅ DB에 비밀번호 제외 UPDATE
            try:
                conn = get_connection()
                cursor = conn.cursor()
                sql = """
                    UPDATE users
                    SET name=%s, phone=%s, birthdate=%s, email=%s
                    WHERE userid=%s
                """
                cursor.execute(sql, (new_name, new_phone, new_birthdate_formatted, new_email, current_userid))
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                flash(f'회원정보 수정 중 오류 발생: {e}', 'error')
                return render_template('modify.html', user=user_info)

        if password_changed:
            flash('회원 정보 및 비밀번호가 성공적으로 수정되었습니다.', 'success')
        else:
            flash('회원 정보가 성공적으로 수정되었습니다.', 'success')

        return redirect(url_for('users_profile_bp.profile'))

    return render_template('modify.html', user=user_info)
