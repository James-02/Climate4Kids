# IMPORTS
from datetime import datetime
from flask import Blueprint, render_template
from models import User, Student, Group
from forms import GroupRegistrationForm
from random import randint
from app import db
# CONFIG
users = Blueprint('users', __name__, template_folder='templates')

# Read Dictionary
# REFERENCE: https://eslgrammar.org/list-of-nouns/#List_of_Nouns_in_English
with open("static/dict.txt", "r") as r:
    words = r.readlines()


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
    form = GroupRegistrationForm()
    if form.validate_on_submit():
        group_id = randint(111111, 999999)
        id_check = Group.query.filter_by(id=group_id).first()

        # checks if the ID exists and reruns the method if it does
        if id_check:
            create_group()

        else:
            db.session.add(Group(id, form.name, form.size))
            db.session.commit()
            return render_template('auth/create_group.html', form=form)


@users.route('/create_students', methods=['GET'])
def create_students():
    with open("test.txt", "r") as r:
        for name in r.readlines():
            username, password = generate_account(name)
            print(username)
            print(password)
            db.session.add(User("student", name, username, password, None, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            db.session.commit()
    return render_template('auth/create_students.html')


def generate_account(name):
    """ Function to generate a username based on the given input and a password of three random words and 4 random digits,
    the digits will be the same as in the username.
    """
    password = ""
    nums = str(randint(1111, 9999))
    username = str(name.strip().replace(" ", "")) + nums
    if User.query.filter_by(username=username).first():
        generate_account(name)

    for _ in range(3):
        password += words[randint(0, len(words) - 1)].replace("\n", "")
    password += nums

    return username, password
