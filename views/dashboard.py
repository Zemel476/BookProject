from flask import Blueprint, render_template

from utils.db_util import DBUtil

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/get_dashboard', methods=['GET', 'POST'])
def get_dashboard():
    sql = "select count(1) from borrow_records where status = 3"
    with DBUtil() as db:
        count = db.cursor.execute(sql)

    return render_template('dashboard/dashboard.html', count=count)


@bp.route('/borrow', methods=['GET', 'POST'])
def borrow():
    """借阅"""
    with DBUtil() as db:
        sql = 'select book_id, title from books'
        books = db.fetch_all(sql)

    return render_template('dashboard/borrow.html', books=books)


@bp.route('/renewal', methods=['GET', 'POST'])
def renewal():
    """续借"""
    return render_template('dashboard/renewal.html')


@bp.route('/giveback', methods=['GET', 'POST'])
def giveback():
    """归还"""
    return render_template('dashboard/giveback.html')