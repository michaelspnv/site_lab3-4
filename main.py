from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from dotenv import load_dotenv
from models import db, login, UserModel
from os import getenv

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = getenv('SECRET_KEY')
app.config.from_object('config.Config')

db.init_app(app)
login.init_app(app)
login.login_view = 'login'


@app.before_request
def create_table():
    db.create_all()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/content')
    return render_template('index.html')


@app.route('/index')
def index_redirect():
    return redirect(url_for('index'))


@app.route('/', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 3 or len(password) < 3:
            message = 'Username/password should contain at least 3 characters!'
            return render_template('index.html', ans=message)

        if UserModel.query.filter_by(username=username).first():
            message = 'Username already taken.'
            return render_template('index.html', ans=message)

        user = UserModel(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login', success=True))
    return render_template('index.html')


@app.route('/login')
def login_template():
    if current_user.is_authenticated:
        return redirect('/content')
    success = request.args.get('success')
    message = ''
    if success:
        message = 'You have successfully registered.'
    return render_template('login.html', ans=message)


@app.route('/login', methods=["POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = UserModel.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect('/content')
        message = 'User not found.'
        return render_template('login.html', ans=message)
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/index')


@app.route('/content')
@login_required
def content():
    return render_template('content.html')


if __name__ == '__main__':
    app.run()
