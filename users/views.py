# IMPORTS
from flask import Blueprint, render_template

# CONFIG
users = Blueprint('users', __name__, template_folder='templates')


# VIEWS
@users.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template('auth/registration.html')


@users.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')


@users.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


@users.route('/account', methods=['GET'])  # TODO: Change /profile to /<user id>
def account():
    return render_template('account.html')


@users.route('/content', methods=['GET'])
def content():
    return render_template('content.html')


@users.route('/create_group', methods=['GET'])
def create_group():

    return render_template('auth/create_group.html')
