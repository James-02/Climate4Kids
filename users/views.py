# IMPORTS
from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_user, current_user
from wtforms.fields.core import Label
from werkzeug.security import check_password_hash
from werkzeug.datastructures import MultiDict

from models import User
from users.forms import LoginForm, QuizQuestion

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
        if current_user.user_type == 'teacher':  # this may need changing
            return redirect('templates/dashboard.html')
        else:
            return redirect('templates/content.html')

    return render_template('auth/login.html', form=form)


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


# no button for this url yet so needs to be access directly through URL
# question_id is just a proof of concept for getting the desired question and can be left as anything e.g. 01
@users.route('/quiz_question/<question_id>', methods=['POST', 'GET'])
def quiz_question(question_id):
    # should probably be done with a database. Select the desired question data - ASK IN MEETING
    # question = string
    # choices = list or dict - ASK IN MEETING
    # answer = int (probably) - ASK IN MEETING

    # Examples
    question = "Which of these does not fit?"
    choices = ("1", "Dog"), ("2", "Cat"), ("3", "Fish")
    answer = "3"

    form = QuizQuestion()
    # define the question label and answers
    form.question.label = Label("question", question + " ID: " + question_id)
    form.radio_field.choices = choices

    if form.validate_on_submit():
        print(form.radio_field.data)
        if form.radio_field.data == answer:
            print("Correct answer")
            # handle correct answer
            # could be held as session data then updated to database upon completion - would then have to reveal
            #   correct answers at the end of the test to prevent cheating.

        else:
            print("Incorrect answer")
            # handle incorrect answer

        # rendering next question - question ID's could be of the format XX-YY where XX is the quiz ID and YY is
        #   the question ID, this way we could move to the next question by simply incrementing the quiz ID. Ending
        #   the quiz could then be indicated by the question_id returning null when requested from the database
        next_question_id = int(question_id) + 1
        return redirect(f"/quiz_question/{next_question_id}")

    return render_template('quiz_question.html', form=form)


"""
Useful explanation of querying with Inheritance: https://docs.sqlalchemy.org/en/14/orm/inheritance_loading.html
"""
