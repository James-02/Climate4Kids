# IMPORTS
from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_user, current_user
from wtforms.fields.core import Label
from werkzeug.security import check_password_hash
from werkzeug.datastructures import MultiDict
from flask_navigation import Navigation

from models import User, Student, Teacher, Quiz, Question, StudentQuizScores, Group
from users.forms import LoginForm, QuizForm

from app import db, app

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


# Displays all the quizzes available to the current user
@users.route('/quizzes', methods=['GET', 'POST'])
def quizzes():
    # displays all the quizzes available to the user, that is, quizzes under the same key stage as the user's group
    available_quizzes = []
    for s, q, g in db.session.query(Student, Quiz, Group).filter(Student.id == 2,
                                                                 Group.id == Student.group_id,
                                                                 Quiz.key_stage == Group.key_stage).all():
        available_quizzes.append((q.id, q.name))

    with app.app_context():
        nav = Navigation()
        nav.init_app(app)

        nav_items = []

        for quiz in available_quizzes:
            nav_items.append(nav.Item(quiz[1], 'users.quiz_questions', {'quiz_id': quiz[0]}))

        nav.Bar('quiz_navbar', nav_items)

        return render_template('quizzes.html')


@users.route('/quiz_questions/<int:quiz_id>', methods=['POST', 'GET'])
def quiz_questions(quiz_id):
    # Example
    # question = "Which of these is a Fish?"
    # choices = "Dog|Cat|Fish|Wolf|Bear"
    # correct_choice = 2

    # get all questions for the specified quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # define the question label and choices for each question
    form = QuizForm(request.form)
    question_num = 0
    for question in questions:
        form.questions[question_num].question_text.label = Label("question_text", question.question_text)
        # convert the string choices into the appropriate format
        choices = question.choices.split("|")
        radio_field_choices = []
        answer_count = 0
        for choice in choices:
            # set the hidden value 'correct' as True for the correct answer
            correct = (answer_count == question.correct_choice)
            radio_field_choices.append((correct, choice))
            answer_count += 1

        form.questions[question_num].radio_field.choices = radio_field_choices
        question_num += 1

    if form.validate_on_submit():
        # calculate the score and add to the StudentQuizScores table
        correct_answers = 0
        for question in form.questions.data:
            if question['radio_field'] == 'True':
                correct_answers += 1
        score = (correct_answers / 5) * 100

        # TODO: Update to use current_user to get the student_id
        # saves student's quiz score to database
        quiz_score = StudentQuizScores(quiz_id=quiz_id, student_id=2, score=score)
        db.session.add(quiz_score)
        db.session.commit()

        return render_template('quiz_results.html', quiz_score=score)

    return render_template('quiz_question.html', form=form)


"""
Useful explanation of querying with Inheritance: https://docs.sqlalchemy.org/en/14/orm/inheritance_loading.html
"""
