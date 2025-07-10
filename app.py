from flask import Flask, session, request, redirect, url_for

# 不需要登录的白名单（路由端点名）
LOGIN_EXEMPT_ROUTES = {'auth.login', 'public_page'}


def check_login():
    # 确保正确获取当前请求的端点
    current_endpoint = request.endpoint

    # 1. 检查是否在白名单中
    if current_endpoint and current_endpoint in LOGIN_EXEMPT_ROUTES:
        return  # 放行白名单路由

    # 2. 静态文件特殊处理
    if request.path.startswith('/static/'):
        return  # 放行静态资源

    # 检查 session 中是否有登录标识
    if session.get('account'):
        if request.path == '/' or current_endpoint == 'auth.login':
            return redirect('dashboard/get_dashboard')

        return

    return redirect(url_for('auth.login', next=request.url))


def get_user_name():
    account = session['account']

    return account['name']

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

    app.before_request(check_login)

    app.template_global()(get_user_name)

    from views import auth
    app.register_blueprint(auth.bp)

    from views import books
    app.register_blueprint(books.bp)

    from views import borrow
    app.register_blueprint(borrow.bp)

    from views import dashboard
    app.register_blueprint(dashboard.bp)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
