# IMPORTS
from flask import Blueprint, render_template, redirect, flash
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash

from models import User
from users.forms import LoginForm

# CONFIG
users = Blueprint('users', __name__, template_folder='templates')


# VIEWS
@users.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template('auth/registration.html')


@users.route('/login', methods=['GET', 'POST'])
def login():
    # create login form object
    form = LoginForm()

    if form.validate_on_submit():

        print(form.username.data)
        print(form.password.data)

        # get user (if they exist) by their username
        user = User.query.filter_by(username=form.username.data).first()

        # check if user has entered valid credentials
        if not user or not check_password_hash(user.password, form.password.data):
            # flash a warning message and reload the page if credentials are invalid
            flash('Incorrect Username or Password, please try again')
            return render_template('auth/login.html', form=form)

        # login the user
        login_user(user)

        # redirect the user to the appropriate page for their role
        if current_user.user_type == 'teacher':     # this may need changing
            return redirect('templates/dashboard.html')
        else:
            return redirect('templates/content.html')

    return render_template('auth/login.html', form=form)


@users.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


@users.route('/content', methods=['GET'])
def content():
    return render_template('content.html')



"""
Useful explanation of querying with Inheritance: https://docs.sqlalchemy.org/en/14/orm/inheritance_loading.html
"""