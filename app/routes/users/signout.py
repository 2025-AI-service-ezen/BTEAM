from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection  # DB 연결 함수 (오타 주의)

bp = Blueprint('users_signout_bp', __name__)

@bp.route('/signout', methods=['GET', 'POST'])
def signout():
    if 'user' not in session:
        return redirect(url_for('users_login_bp.login'))  # 로그인 안 된 경우 로그인 페이지로

    if request.method == 'POST':
        user_id = session['user']  # 로그인된 사용자 ID

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # favorites 테이블에서 해당 사용자 삭제
                # delete_favorites_sql = "DELETE FROM favorites WHERE userid = %s"
                # cursor.execute(delete_favorites_sql, (user_id,))

                # users 테이블에서 해당 사용자 삭제
                delete_user_sql = "DELETE FROM users WHERE userid = %s"
                cursor.execute(delete_user_sql, (user_id,))

            conn.commit()
        except Exception as e:
            conn.rollback()
            print("회원 탈퇴 중 오류:", e)
        finally:
            conn.close()

        # 세션에서 사용자 제거
        session.pop('user', None)

        # 탈퇴 후 메인 페이지로 리다이렉트
        return redirect(url_for('web_index_bp.index'))

    # GET 요청이면 탈퇴 확인 페이지 보여줌
    return render_template('signout.html')
