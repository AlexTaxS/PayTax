from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, escape, send_file
from flask_script import Manager, Command, Shell
from forms import ContactForm, LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate, MigrateCommand
from threading import Thread
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from time import time
import smtplib
import datetime
from flask import copy_current_request_context
from datetime import date, datetime, timedelta
#import mysql.connector
import tempfile
from string import ascii_uppercase
from threading import Thread
import jwt


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'a really key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_app_db.db'
app.config['MAIL_DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app,  db)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Faker(Command):
    'Команда для добавления поддельных данных в таблицы'
    def run(self):
        #логика функции
        print("Fake data entered")


def shell_context():
    import os, sys
    return dict(app=app, os=os, sys=sys)

manager.add_command("shell", Shell(make_context=shell_context))



@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    return "Profile page of user #{}".format(user_id)

@app.route('/books/<genre>')
def books(genre):
    return "All Books in {} category".format(genre)

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена")

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # здесь должна быть проверка корректности введенных данных
        try:
            hash = generate_password_hash(form.password.data)
            u = User(username=form.username.data, email=form.email.data, password_hash=hash)
            #u.set_password(hash)            
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
            flash("Указана почта, которая уже зарегистрирована", 'error')
            return redirect(url_for('register'))
 
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/')
def home():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))

        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/downloadenvd')
@login_required
def download_fileenvd():
    p = "Doc/Письмо ФНС СД 4 3 19053.rtf"    
    return send_file(p, as_attachment=True)


@app.route('/begin')
@login_required
def begin():
    return render_template('begin.html')


@app.route('/cookie/')
def cookie():
    if not request.cookies.get('foo'):
        res = make_response("Setting a cookie")
        res.set_cookie('foo', 'bar', max_age=60*60*24*365*2)
    else:
        res = make_response("Value of cookie foo is {}".format(request.cookies.get('foo')))
    return res

@app.route('/delete-cookie/')
def delete_cookie():
    res = make_response("Cookie Removed")
    res.set_cookie('foo', 'bar', max_age=0)
    return res

@app.route('/article/', methods=['POST',  'GET'])
def article():
    if request.method == 'POST':
        print(request.form)
        res = make_response("")
        res.set_cookie("font", request.form.get('font'), 60*60*24*15)
        res.headers['location'] = url_for('article')
        return res, 302

    return render_template('article.html')

@app.route('/visits-counter/')
def visits():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1  # чтение и обновление данных сессии
    else:
        session['visits'] = 1  # настройка данных сессии
    return "Total visits: {}".format(session.get('visits'))

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='category', cascade='all,delete-orphan')

    def __repr__(self):
        return "<{}:{}>".format(id, self.name)

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))

    def __repr__(self):
        return "<{}:{}>".format(self.id,  self.title[:10])

class  Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', secondary=post_tags, backref='tags')

    def __repr__(self):
        return "<{}:{}>".format(id, self.name)


class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    designation = db.Column(db.String(255), nullable=False)
    doj = db.Column(db.Date(), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,  password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    

@app.route('/session/')
def updating_session():
    res = str(session.items())

    cart_item = {'pineapples': '10', 'apples': '20', 'mangoes': '30'}
    if 'cart_item' in session:
        session['cart_item']['pineapples'] = '100'
        session.modified = True
    else:
        session['cart_item'] = cart_item

    return res



@app.route('/search4', methods=['POST'])
@login_required
def do_search() -> 'html':    
    activity = request.form['activity']
    region = request.form['region']
    revenue = int(request.form['revenue'])
    staff = request.form['staff']
    num_empl = int(request.form['num_empl'])
    amount_exp = request.form['amount_exp']
    advocate = request.form['advocate']
    contr_partn = request.form['contr_partn']

    okvd1 = ['64.92', '64.92.1', '64.92.2', '64.92.3', '64.92.4',
             '64.92.6', '64.92.7']
    
             

    title = 'Для вас подобран следующий режим налогов:'

    if activity in okvd1:
        results = str("Может применяться только ОСН")
              
    elif advocate == '1':
         results = str("Может применяться только режим для адвокатов и нотариусов")
                 
    elif revenue >= 150000000:
          results = str("Может применяться только ОСН")
                   
    elif num_empl >= 100:
          results = str("Может применяться только ОСН")
                   
    elif contr_partn == '1':
          results = str("Может применяться УСН 15%")
          
    elif amount_exp == '1':
           results = str("Может применяться УСН 15%")
         
    elif amount_exp == '0':
           results = str("Можете применяться УСН 6%")
           
    elif revenue <= 2400000 and num_empl == 0:
           results = str("Может применяться НПД")
           

    elif revenue <= 60000000 and num_empl <= 15 and activity in okvd4:
           results = str("Может применяться ПСН")


    else:
        results = str("Может применяться УСН")        

    
    return render_template('results.html',
                           the_title=title,
                           the_activity=activity,
                           the_region=region,
                           the_revenue=revenue,
                           the_staff=staff,
                           the_num_empl=num_empl,
                           the_amount_exp=amount_exp,
                           the_advocate=advocate,
                           the_contr_partn=contr_partn,
                           the_results=results,)


@app.route('/admin/')
#@login_required
def admin():
    return render_template('admin.html')


@app.route('/delete-visits/')
def delete_visits():
    session.pop('visits', None)  # удаление данных о посещениях
    return 'Visits deleted'

if __name__ == "__main__":
    manager.run()
