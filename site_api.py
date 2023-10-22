import flask
from datetime import datetime
from data import db_session
from data.analyzes import Analysis
from data.users import User
from data.orders import Order
from flask import jsonify
from flask_paginate import Pagination
from flask import render_template, request, redirect
from flask_login import login_required, current_user


PERPAGE = 10  # позиций на страницу при пагинации (pagination)

# расширяющий эскиз для панели администрирования
blueprint = flask.Blueprint('site_api', __name__, template_folder='templates')


# главная страница администрирования
@blueprint.route('/api/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    if current_user.is_admin():
        a_json = jsonify({'status': 'index', 'action': ['analysis', 'orders', 'users']})
        return render_template('admin/index.html', title='Админ панель', data='Выбор действия', a_json=a_json.json)
    else:
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель',
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)


# пользователи
@blueprint.route('/api/admin/users')
@blueprint.route('/api/admin/users/<int:page>')
@login_required
def get_users(page=1):
    offset = PERPAGE * (page - 1)
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель',
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    users = db_sess.query(User.id, User.email, User.name, User.lastname,
                          User.birthday, User.gender, User.level, User.created_date).order_by(User.name).all()
    if not users:
        total = 0
        a_json = jsonify({'status': 'error', 'errormsg': 'Перечень пользователей пуст!'})
    else:
        result = {}
        total = len(users)
        for user in users[offset: offset + PERPAGE]:
            result[user.id] = [user.email, user.name, user.lastname,
                               user.birthday, user.gender,  user.level,
                               user.created_date.strftime('%d.%m.%Y в %H:%M')]
        a_json = jsonify({'status': 'users', 'result': result})
    pagination = Pagination(page=page, per_page=PERPAGE, total=total,
                            items=users[offset: offset + PERPAGE],
                            css_framework='bootstrap5')
    return render_template('/admin/index.html', title='Админ панель',
                           data='Пользователи', a_json=a_json.json,
                           page=page, per_page=PERPAGE, pagination=pagination)


# удаление пользователя
@blueprint.route('/api/admin/users/del/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель', crumb=['users', 'Пользователи'],
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    role = db_sess.query(User).get(user_id)
    if not role:
        a_json = jsonify({'status': 'error', 'errormsg': f'Записи c номером {user_id} не существует!'})
    else:
        # если предпринята попытка удалить админа по прямой ссылке
        if role.level == 2:
            a_json = jsonify({'status': 'error', 'errormsg': 'Удаление администратора невозможно!'})
        else:
            orders = db_sess.query(Order).filter(Order.user_id == user_id).all()
            db_sess.delete(role)
            if orders:
                for order in orders:
                    db_sess.delete(order)
            db_sess.commit()
            return redirect('/api/admin/users')
    return render_template('/admin/index.html', title='Админ панель', crumb=['users', 'Пользователи'],
                           data=f'Запись {user_id} не была удалена',
                           a_json=a_json.json)


# заказы пользователей
@blueprint.route('/api/admin/orders')
@blueprint.route('/api/admin/orders/<int:page>')
@login_required
def get_orders(page=1):
    offset = PERPAGE * (page - 1)
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель',
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    found_order = request.args.get('num_order')
    if found_order:
        if len(list(found_order)) > 30:
            a_json = jsonify({'status': 'error', 'errormsg': 'Недопустимое количество введённых символов!'})
            return render_template('/admin/index.html', title='Админ панель',
                                   crumb=['orders', 'Заказы'], data='Ошибка при поиске заказа',
                                   a_json=a_json.json)
        result = {}
        db_sess = db_session.create_session()
        orders = db_sess.query(Order).filter(Order.num_order.like(f'{found_order.strip()}'))
        if orders.count() > 0:
            total = orders.count()
            for order in orders[offset: offset + PERPAGE]:
                result[order.id] = [order.num_order, order.user.email, order.analiz.name,
                                    order.analiz.price, order.created_date.strftime('%d.%m.%Y')]
            a_json = jsonify({'status': 'orders', 'result': result})
            pagination = Pagination(page=page, per_page=PERPAGE, total=total,
                                    items=orders[offset: offset + PERPAGE],
                                    css_framework='bootstrap5')
            return render_template('/admin/index.html',  title='Админ панель', crumb=['orders', 'Заказы'],
                                   a_json=a_json.json, data=f'Заказ № {found_order}',
                                   page=page, per_page=PERPAGE, pagination=pagination)
        a_json = jsonify({'status': 'error', 'errormsg': f'Заказ № {found_order} не найден!'})
        return render_template('/admin/index.html', crumb=['orders', 'Заказы'],
                               title='Админ панель', data='Поиск заказа по номеру', a_json=a_json.json)
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).order_by(Order.id).all()
    if not orders:
        total = 0
        a_json = jsonify({'status': 'error', 'errormsg': 'Заказов ещё нет.'})
    else:
        result = {}
        total = len(orders)
        for order in orders[offset: offset + PERPAGE]:
            result[order.id] = [order.num_order, order.user.email,
                                order.analiz.name, order.analiz.price, order.created_date.strftime('%d.%m.%Y')]
        a_json = jsonify({'status': 'orders', 'result': result})
    pagination = Pagination(page=page, per_page=PERPAGE, total=total,
                            items=orders[offset: offset + PERPAGE],
                            css_framework='bootstrap5')
    return render_template('/admin/index.html', title='Админ панель', data='Заказы',
                           a_json=a_json.json, page=page, per_page=PERPAGE, pagination=pagination)


# удаление заказа
@blueprint.route('/api/admin/orders/del/<int:order_id>', methods=['GET'])
@login_required
def delete_order(order_id):
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель', crumb=['users', 'Пользователи'],
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    role = db_sess.query(Order).get(order_id)
    if not role:
        a_json = jsonify({'status': 'error', 'errormsg': f'Записи c номером {order_id} не существует!'})
    else:
        db_sess.delete(role)
        db_sess.commit()
        return redirect('/api/admin/orders')
    return render_template('/admin/index.html', title='Админ панель', crumb=['users', 'Пользователи'],
                           data=f'Запись {order_id} не была удалена',
                           a_json=a_json.json)


# исследования
@blueprint.route('/api/admin/analysis')
@blueprint.route('/api/admin/analysis/index')
@blueprint.route('/api/admin/analysis/index/<int:page>')
@login_required
def get_analysis(page=1):
    offset = PERPAGE * (page - 1)
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель',
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    tests = db_sess.query(Analysis).all()
    result = {}
    total = len(tests)
    for test in tests[offset: offset + PERPAGE]:
        result[test.id] = [test.name, test.price, test.created_date.strftime('%d.%m.%Y')]
    a_json = jsonify({'status': 'analysis', 'result': result})
    pagination = Pagination(page=page, per_page=PERPAGE, total=total,
                            items=tests[offset: offset + PERPAGE],
                            css_framework='bootstrap5')
    return render_template('/admin/index.html', title='Админ панель', data='Исследования',
                           page=page, per_page=PERPAGE, pagination=pagination, a_json=a_json.json)


# добавление нового исследования
@blueprint.route('/api/admin/analysis/create', methods=['GET', 'POST'])
@login_required
def add_test():
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    query = db_sess.query(Analysis).all()
    list_name = [item.name for item in query]
    if not query:
        new_id = 1
    else:
        id_list = [item.id for item in query]
        new_id = max(id_list) + 1
    a_json = jsonify({'status': 'create', 'test': new_id})
    if request.method == "POST":
        id = request.form.get('id')
        name = request.form.get('name')
        try:
            price = int(request.form.get('price'))
            if price <= 0 or price > 1000000:
                raise ValueError
        except ValueError:
            a_json = jsonify({'status': 'error',
                              'errormsg': 'Цена должна быть положительным числом:'
                                          ' больше 0, но не превышать 1000000 руб.'})
            return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                                   data='Добавление нового исследования', a_json=a_json.json)
        if not name:
            a_json = jsonify({'status': 'error', 'errormsg': 'Пустое значение для нового исследования!'})
        elif len(list(name)) > 50:
            a_json = jsonify({'status': 'error', 'errormsg': 'Очень много символов в название услуги!'})
        elif name in list_name:
            a_json = jsonify({'status': 'error', 'errormsg': 'Исследование с таким наименованием уже существует!'})
        else:
            item = Analysis(id=id, name=name, price=price)
            try:
                db_sess.add(item)
                db_sess.commit()
                return redirect('/api/admin/analysis')
            except:
                a_json = jsonify({'status': 'error', 'errormsg': 'Запись не добавлена!'})
    return render_template('/admin/index.html', title='Админ панель',
                           crumb=['analysis', 'Исследования'], data='Добавление нового исследования',
                           a_json=a_json.json)


# удаление исследования
@blueprint.route('/api/admin/analysis/del/<int:test_id>', methods=['GET'])
@login_required
def delete_test(test_id):
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    test = db_sess.query(Analysis).get(test_id)
    print(test)
    if not test:
        a_json = jsonify({'status': 'error', 'errormsg': f'Записи c номером {test_id} не существует!'})
    else:
        db_sess.delete(test)
        db_sess.commit()
        return redirect('/api/admin/analysis')
    return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                           data=f'Запись {test_id} не была удалена',
                           a_json=a_json.json)


# редактирование исследования
@blueprint.route('/api/admin/analysis/edit/<int:test_id>', methods=['GET', 'POST'])
@login_required
def edit_test(test_id):
    if not current_user.is_admin():
        a_json = jsonify({'status': 'error', 'errormsg': f'{current_user.name}, Вы не являетесь админом!'})
        return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                               data='Недостаточный уровень прав доступа', a_json=a_json.json)
    db_sess = db_session.create_session()
    test = db_sess.query(Analysis).get(test_id)
    query = db_sess.query(Analysis).all()
    name_list = [item.name for item in query]
    if not test:
        a_json = jsonify({'status': 'error', 'errormsg': 'Исследование не найдено!'})
        return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                               data='Редактирование исследования', a_json=a_json.json)

    if request.method == "POST":
        id = request.form.get('id')
        try:
            name = request.form.get('name')
            if len(name) > 50 or len(name) == 0:
                raise Exception
        except Exception:
            a_json = jsonify({'status': 'error',
                              'errormsg': 'Наименование услуги не должна быть пустой и превышать 50 символов!'})
            return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                                   data='Редактирование исследования', a_json=a_json.json)
        try:
            price = int(request.form.get('price'))
            if price <= 0 or price > 1000000:
                raise ValueError
        except ValueError:
            a_json = jsonify({'status': 'error',
                              'errormsg': 'Цена должна быть положительным числом:'
                                          ' больше 0, но не превышать 1000000 руб.'})
            return render_template('/admin/index.html', title='Админ панель',
                                   crumb=['analysis', 'Исследования'],
                                   data='Редактирование исследования', a_json=a_json.json)
        if name == test.name and price == test.price:
            a_json = jsonify({'status': 'error', 'errormsg': 'Вы не изменили данные!'})
            return render_template('/admin/index.html', title='Админ панель',
                                   crumb=['analysis', 'Исследования'],
                                   data='Редактирование исследования', a_json=a_json.json)
        if name in name_list and price == test.price:
            a_json = jsonify({'status': 'error', 'errormsg': 'Исследование с таким наименованием уже существует!'})
            return render_template('/admin/index.html', title='Админ панель',
                                   crumb=['analysis', 'Исследования'],
                                   data='Редактирование исследования', a_json=a_json.json)
        db_sess.query(Analysis).filter(Analysis.id == id).update({Analysis.name: name,
                                                                  Analysis.price: price,
                                                                  Analysis.created_date: datetime.now()},
                                                                 synchronize_session=False)
        db_sess.commit()
        return redirect('/api/admin/analysis')
    a_json = jsonify({'status': 'edit', 'test': {'id': [test.id, 'hidden'],
                                                 'name': [test.name, 'text'], 'price': [test.price, 'text']}})
    return render_template('/admin/index.html', title='Админ панель', crumb=['analysis', 'Исследования'],
                           data='Редактирование исследования',
                           a_json=a_json.json)
