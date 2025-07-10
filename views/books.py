import math
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from utils.db_util import DBUtil

bp = Blueprint('books', __name__, url_prefix='/books')


@bp.route('/get_books', methods=['GET', 'POST'])
def get_books():
    page_index = request.args.get('page', 1, type=int)
    if page_index < 1:
        page_index = 1

    page_size = 2

    all_count_sql = "select count(1) as count from books;"
    book_sql = "select * from books order by book_id asc limit %s, %s;"

    with DBUtil() as db:
        result = db.fetch_one(all_count_sql)
        # 计算当前显示的页码范围
        page_count = math.ceil(result['count'] / page_size)

        if page_index > page_count:
            page_index = page_count

        book_params = ((page_index - 1) * page_size, page_size)
        books = db.fetch_all(book_sql, book_params)

        book_status = {
            1: '开放',
            2: '未开放',
        }

    return render_template('books/books.html', books=books, book_status=book_status, page_count=page_count, page_index=page_index)


@bp.route('/del_book/<int:book_id>', methods=['GET'])
def del_book(book_id):
    message = ''
    if not book_id:
        return redirect(url_for('books.get_books'))

    del_sql = 'delete from books where book_id = %s'
    del_params = (book_id,)
    with DBUtil() as db:
        db. delete(del_sql, del_params)

        return redirect(url_for('books.get_books'))


@bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    message = ''
    if request.method == 'GET':
        message = "接口请求异常"
        return jsonify(message=message)

    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    publish_date = request.form.get('publish_date')
    isbn = request.form.get('isbn')
    category = request.form.get('category')
    location = request.form.get('location')
    status = request.form.get('status')
    count = request.form.get('count')

    if int(count)< 1 or not title:
        message = "数据异常！"
        return render_template('books/books.html', message=message)

    if publish_date:
        publish_date = datetime.strptime(publish_date, '%Y-%m-%d')
    else:
        publish_date = None

    insert_sql = ("INSERT INTO BOOKS(isbn, title, author, publisher, publish_date, category, status, location, count)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    insert_params = (isbn, title, author, publisher, publish_date, category, status, location, count)

    with DBUtil() as db:
        db.insert(insert_sql, insert_params)

    message = "添加成功！"

    return jsonify(message=message)

@bp.route('/edit_book_view', methods=['GET'])
def edit_book_view():
    book_id = request.args.get('book_id')
    if not book_id:
        return redirect(url_for('books.get_books'))

    query_sql = 'select * from books where book_id = %s'
    query_params = (book_id,)
    with DBUtil() as db:
        book_data = db.fetch_one(query_sql, query_params)
        book_data['publish_date'] = book_data['publish_date'].strftime('%Y-%m-%d')
        return jsonify(book_data=book_data)


@bp.route('/edit_book', methods=['GET', 'POST'])
def edit_book():
    message = ''
    if request.method == 'GET':
        message = "接口请求异常"
        return jsonify(message=message)

    book_id = request.form.get('book_id')
    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    publish_date = request.form.get('publish_date')
    isbn = request.form.get('isbn')
    category = request.form.get('category')
    location = request.form.get('location')
    status = request.form.get('status')
    count = request.form.get('count')

    if int(count) < 1 or not title:
        message = "数据异常！"
        return render_template('books/books.html', message=message)

    if publish_date:
        publish_date = datetime.strptime(publish_date, '%Y-%m-%d')
    else:
        publish_date = None

    update_sql = ("UPDATE BOOKS SET isbn = %s, title = %s, author = %s, publisher = %s, publish_date = %s, "
                  "category = %s, status = %s, location = %s, count = %s WHERE book_id = %s")
    update_params = (isbn, title, author, publisher, publish_date, category, status, location, count, book_id)

    with DBUtil() as db:
        db.insert(update_sql, update_params)

    message = "添加成功！"

    return jsonify(message=message)