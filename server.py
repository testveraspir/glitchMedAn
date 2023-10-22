import site_api
from flask import Flask, render_template, flash, redirect, request, session
from flask_login import LoginManager, current_user, login_required, logout_user, login_user
from data import db_session
from data.analyzes import Analysis
from data.orders import Order
from data.users import User
from forms.loginform import LoginForm
from forms.user import RegisterForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'short secret key'  # для защиты от межсайтовых подделок

# создаём объект менеджера авторизации пользователя
# и приписываем его к нашему приложению
login_manager = LoginManager()
login_manager.init_app(app)

# функция получения данных пользователя

summ_order = 0  # переменная содержит итоговую сумму в корзине
count = 0  # количество исследований в корзине


# следующая error 404 (не авторизован, попытка входа по прямой ссылке)
@app.errorhandler(401)
def http_401_handler(error):
    flash('Пожалуйста, авторизируйтесь!!!', 'danger')
    return redirect('/login')  # надо авторизоваться


@app.errorhandler(404)
def http_404_handler(error):
    return redirect('/error')


@app.errorhandler(500)
def http_500_handler(error):
    return redirect('/error')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/error')
def well():
    return render_template('well.html', title='Ошибка')


@app.route('/')
def index():
    found = request.args.get('substring')
    if found:
        if len(list(found)) > 20:
            flash('В поисковик Вы можете ввести не больше 20 символов!', 'danger')
            return render_template('index.html', title='Главная страница', count=count)
        params = {}
        db_sess = db_session.create_session()
        tests = db_sess.query(Analysis).filter(Analysis.name.like(f'%{found}%')
                                               | Analysis.name.like(f'%{found.capitalize()}%'))
        if tests.count() > 0:
            params['found'] = f'Результаты поиска: {found}'
            params['tests'] = tests
            return render_template('analyzes.html', title='Главная страница', **params, count=count)
        else:
            flash(f'Результаты поиска: {found} не найден', 'danger')
            return render_template('index.html', title='Главная страница', count=count)
    else:
        return render_template('index.html', title='Главная страница', count=count)


@app.route('/analyzes')
def get_analysis():
    db_sess = db_session.create_session()
    tests = db_sess.query(Analysis).all()
    return render_template('analyzes.html', title='Анализы', tests=tests, count=count)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash('Пароли не совпадают!', 'danger')
            return render_template('register.html', title='Регистрация', form=form)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            flash('Такой пользователь уже существует', 'danger')
            return render_template('register.html', title='Регистрация', form=form)
        user = User(name=form.name.data, email=form.email.data, lastname=form.lastname.data,
                    birthday=form.birthday.data, gender=form.gender.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        flash('Процедура регистрации прошла успешно!', 'info')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    global count
    logout_user()
    flash('Вы вышли', 'info')
    session.pop('cart', None)
    count = 0
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вы успешно вошли', 'success')
                return redirect('/')
            flash('Неверная пара: логин - пароль!!!', 'danger')
            render_template('login.html', title='Авторизация',
                            message='Неверный логин или пароль', form=form)
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_to_cart/<int:test_id>')
def add_to_cart(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Analysis).filter(Analysis.id == test_id).first()
    name = test.name
    price = test.price
    # Получение существующей корзины или создание новой
    cart = session.get('cart', {})
    if name not in cart:
        cart[name] = cart.get(name, [test_id, price])
    else:
        flash(f'Исследование: {name} уже есть в корзине!', 'danger')
        return redirect('/analyzes')
    # Сохранение корзины в сессии
    session['cart'] = cart
    return redirect('/cart')


@app.route('/delete')
def delete_visits():
    global count
    session.pop('cart', None)  # удаление данных
    flash('Вы очистили корзину.', 'success')
    count = 0
    return redirect('/cart')


@app.route('/del/<int:test_id>')
def del_from_cart(test_id):
    del_el = ''
    cart = session.get('cart', {})
    for name, el in cart.items():
        if el[0] == test_id:
            del_el = name
            break
    cart.pop(del_el, None)
    print(f'корзина после удаления {cart}')
    session['cart'] = cart
    return redirect('/cart')


@app.route('/cart')
def show_cart():
    global summ_order
    global count
    total = 0
    count = 0
    cart = session.get('cart', {})
    for el in cart.values():
        total += el[1]
        count += 1
    summ_order = round(total * 0.9)
    return render_template('cart.html', title='Корзина', cart=cart, total=total, count=count)


@app.route('/order')
@login_required
def order():
    global count
    num_order = str(current_user.id) + '_' + str(datetime.now().microsecond)
    db_sess = db_session.create_session()
    cart = session.get('cart', {})
    for name, lst in cart.items():
        count += 1
        order_lst = Order()
        order_lst.user_id = current_user.id
        order_lst.analiz_id = lst[0]
        order_lst.num_order = num_order
        current_user.order.append(order_lst)
    db_sess.merge(current_user)
    db_sess.commit()
    session.pop('cart', None)
    count = 0
    return render_template('order.html', title='Ваш заказ',
                           summ=summ_order, num_order=num_order, count=count)


@app.route('/cabinet/<int:user_id>')
@login_required
def get_orders(user_id):
    global count
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).filter(Order.user_id == user_id)
    if orders.count() == 0:
        orders = 0
        return render_template('cabinet.html', title='Личный кабинет', orders=orders, count=count)
    return render_template('cabinet.html', title='Личный кабинет', orders=orders, count=count)


if __name__ == '__main__':
    db_session.global_init('db/analiz.db')
    # регистрация api
    app.register_blueprint(site_api.blueprint)
    app.run(port=8000, host='127.0.0.1')
