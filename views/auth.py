from flask import Blueprint, request, render_template, session, redirect, url_for

from utils.db_util import DBUtil

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    account = request.form.get('account')
    password = request.form.get('password')

    if not account or not password:
        return render_template('auth/login.html', message="账号或密码有误！")

    sql = "select * from user where account= %s and password = %s"
    user_datas = DBUtil().fetch_one(sql, [account, password])
    if not user_datas:
        return render_template('auth/login.html', message="账号或密码有误！")

    session['account'] = {'id': user_datas['id'], 'name': user_datas['name'], 'role': user_datas['role']}

    return redirect('dashboard/get_dashboard')


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

