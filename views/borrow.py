import datetime
import math

from flask import Blueprint, render_template, request, redirect

from utils.db_util import DBUtil

bp = Blueprint('borrow', __name__, url_prefix='/borrow')


@bp.route('/get_borrows', methods=['GET', 'POST'])
def get_borrows():
    page_index = request.args.get('page', 1, type=int)
    if page_index < 1:
        page_index = 1

    page_size = 5

    all_record_sql = "select count(1) as count from borrow_records;"
    record_sql = """select a.*, b.title from borrow_records a 
     left join books b on a.book_id = b.book_id
     order by a.status desc
     limit %s, %s;
     """

    with DBUtil() as db:
        result = db.fetch_one(all_record_sql)
        # 计算当前显示的页码范围
        page_count = math.ceil(result['count'] / page_size)
        if page_index > page_count:
            page_index = page_count

        record_params = ((page_index - 1) * page_size, page_size)
        borrows = db.fetch_all(record_sql, record_params)

        status_dict = {
            '1': {'text': '借阅中', 'cls': 'info'},
            '2': {'text': '已归还', 'cls': 'success'},
            '3': {'text': '已逾期', 'cls': 'danger'},
        }

        return render_template('borrow/borrow.html', borrows=borrows, status_dict=status_dict, page_count=page_count, page_index=page_index)


@bp.route('/re_borrow', methods=['POST'])
def re_borrow():
    card_number = request.form.get('card_number')
    borrow_name = request.form.get('borrow_name')
    title = request.form.get('title')
    days = request.form.get('days')

    message = ""
    if not card_number or not borrow_name or not title:
        message = "数据异常！"
        return render_template('dashboard/renewal.html', message=message)

    sql_params = [card_number, borrow_name, title]
    sql = """SELECT a.record_id, a.days, a.status, a.renew_count FROM `borrow_records` a 
    LEFT JOIN books b on b.book_id = a.book_id 
    WHERE a.`status` = 1 a.card_number = %s and a.borrow_name = %s and b.title = %s
    """
    with DBUtil() as db:
        result = db.fetch_all(sql, sql_params)
        if len(result) == 0:
            message = "未查询到 {} - {} - {} 借阅信息。".format(card_number, borrow_name, title)
        elif len(result) > 1:
            message = "数据异常，请联系技术人员。"
        else:
            record_id = result[0]['record_id']
            record_days = result[0]['days'] + int(days)
            renew_count = int(result[0]['renew_count']) + 1
            update_params = (record_days , renew_count, record_id)
            update_sql = "update borrow_records set days = %s, renew_count = %s where record_id = %s"
            db.update(update_sql, update_params)

            message = '{} - {} - {} 续借成功'.format(card_number, borrow_name, title)

        return render_template('dashboard/renewal.html', message=message)


@bp.route('/add_borrow', methods=['POST'])
def add_borrow():
    book_id = request.form.get('book_id')
    card_number = request.form.get('card_number')
    borrow_name = request.form.get('borrow_name')
    department = request.form.get('department')
    days = request.form.get('days')

    message = ""
    if not borrow_name or not card_number or not book_id:
        message = "数据异常！"
        return render_template('dashboard/borrow.html', message=message)

    sql_params = [card_number, borrow_name, book_id]
    sql = """
    SELECT count(1) as 'count' FROM `borrow_records` where card_number = %s and borrow_name = %s and book_id = %s 
    """

    message = ""
    with DBUtil() as db:
        result = db.fetch_one(sql, sql_params)
        if result['count'] != 0:
            message = '{} - {} 已有借阅信息，无法再次借阅。'.format(card_number, borrow_name)
        else:
            now_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            borrow_date = datetime.datetime.strptime(now_date, '%Y-%m-%d %H:%M:%S')
            insert_data = (borrow_name, department, card_number, borrow_date, days, 1, book_id)
            insert_sql = """
            INSERT INTO `borrow_records`(borrow_name, department, card_number, borrow_date, days, status, book_id) 
            values(%s, %s, %s, %s, %s, %s, %s)
            """

            db.insert(insert_sql, insert_data)
            message = "{} - {} 借阅成功".format(card_number, borrow_name)

        return render_template('dashboard/borrow.html', message=message)


@bp.route('/giveback_borrow', methods=['POST'])
def giveback_borrow():
    title = request.form.get('title')
    card_number = request.form.get('card_number')
    borrow_name = request.form.get('borrow_name')

    message = ""
    if not title or not card_number or not borrow_name:
        message = "数据异常！"
        return render_template('dashboard/giveback.html', message=message)

    sql_params = [card_number, borrow_name, title]
    sql = """SELECT a.record_id FROM `borrow_records` a 
    LEFT JOIN books b on b.book_id = a.book_id 
    WHERE a.`status` = 1 and a.card_number = %s and a.borrow_name = %s and b.title = %s
    """

    message = ""
    with DBUtil() as db:
        result = db.fetch_all(sql, sql_params)
        if len(result) == 0:
            message = '{} - {} - {}未查询到借阅信息，请核查。'.format(card_number, borrow_name, borrow_name)
        elif len(result) > 1:
           message = "数据异常，请联系技术人员。"
        else:
           update_params = (2, result[0]['record_id'])
           update_sql = "update borrow_records set status = %s where record_id = %s"
           db.update(update_sql, update_params)

           message = '{} - {} - {} 书籍归还成功'.format(card_number, borrow_name, borrow_name)

    return render_template('dashboard/giveback.html', message=message)