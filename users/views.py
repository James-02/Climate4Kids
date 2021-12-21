# IMPORTS
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from models import User, Student, Group
from forms import CreateGroup, RegisterStudent
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
    teacher_id = 2  # TODO replace with current_user when ready
    groups = Group.query.filter_by(teacher_id=teacher_id).all()
    return render_template('dashboard.html', groups=groups)


@users.route('/account', methods=['GET'])  # TODO: Change /profile to /<user id>
def account():
    return render_template('account.html')


@users.route('/content', methods=['GET'])
def content():
    return render_template('content.html')


@users.route('/groups/<string:group_id>', methods=['GET'])
def group(group_id):
    group_obj = Group.query.get(group_id)
    student_list = Student.query.filter_by(group_id=group_id).all()
    return render_template('groups/group.html',
                           group=group_obj,
                           students=student_list)


@users.route('/groups/<string:group_id>/edit_group', methods=['GET', 'POST'])
def edit_group(group_id):
    form = CreateGroup()
    group = Group.query.get(group_id)
    if form.validate_on_submit():
        values = {'name': form.name.data, 'size': form.size.data, 'key_stage': form.key_stage.data}
        db.session.query(Group).filter_by(id=group_id).update(values)
        db.session.commit()
        return redirect(url_for('users.group', group_id=group_id))
    return render_template('groups/edit_group.html', form=form, group_id=group_id, group=group)


@users.route('/groups/create_group', methods=['GET', 'POST'])
def create_group():
    form = CreateGroup()
    if form.validate_on_submit():
        group_id = randint(111111, 999999)
        id_check = Group.query.filter_by(id=group_id).first()

        # while loop to check that the ID does not already exist
        while id_check:
            group_id = randint(111111, 999999)

        else:
            group = Group(id=group_id, name=str(form.name.data), size=form.size.data, key_stage=form.key_stage.data)
            group.teacher_id = 2  # TODO: Replace this test ID with current_user
            db.session.add(group)
            db.session.commit()
            return redirect(url_for('users.create_students', group_id=group_id))
    return render_template('groups/create_group.html', form=form)


@users.route('/groups/<string:group_id>/create_students', methods=['GET', 'POST'])
def create_students(group_id):
    form = RegisterStudent()
    if form.validate_on_submit():
        names = list(filter(None, (form.names.data.strip().split("\r\n"))))
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        for name in names:
            username, password = generate_account(name)
            student = Student(user_type="student", name=name, username=username, password=password,
                              last_login=None, registered_on=date, group_id=group_id)
            db.session.add(student)
            db.session.commit()
        return redirect(url_for('users.dashboard'))

    return render_template('groups/create_students.html', form=form, group_id=group_id)


def generate_account(name):
    """ Function to generate a username based on the given input and a password of three random words and 4 random digits,
    the digits will be the same as in the username.
    """
    password = ""
    nums = str(randint(1111, 9999))
    username = str(name.strip().replace(" ", "")) + nums
    username_check = User.query.filter_by(username=username).first()

    while username_check:
        nums = str(randint(1111, 9999))

    for _ in range(3):
        password += words[randint(0, len(words) - 1)].replace("\n", "")
    password += nums

    return username, password
