
# IMPORT
import re
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import flash, Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required, logout_user
from wtforms.fields.core import Label
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from models import db, User, Student, Group, Teacher, Quiz, Question, StudentQuizScores
from users.forms import QuizForm, ChangePassword, ForgottenPassword
from auth.forms import LoginForm

from random import randint
from app import app, requires_roles

import logging

# CONFIG
SMTP_EMAIL = app.config['SMTP_EMAIL']
SMTP_PASSWORD = app.config['SMTP_PASSWORD']
users = Blueprint('users', __name__, template_folder='templates')

# Read Dictionary
# REFERENCE: https://eslgrammar.org/list-of-nouns/#List_of_Nouns_in_English
with open("static/dict.txt", "r") as r:
    words = r.readlines()


# VIEWS
@users.route('/dashboard', methods=['GET'])
@login_required
@requires_roles('teacher')
def dashboard():
    groups = Group.query.filter_by(teacher_id=current_user.id).all()
    return render_template('dashboard.html', groups=groups)


@users.route('/account/<string:_username>', methods=['GET'])
@login_required
def account(_username):
    """ Displays the correct account page depending on the user
    """
    if current_user.role == 'student':
        student = Student.query.get(current_user.id)
        group = Group.query.get(student.group_id)
        if group is not None:
            students = len(group.students)
            teacher = Teacher.query.get(group.teacher_id)
            group_average_quiz_score = get_group_average_quiz_score(group.id)
        else:
            flash('You do not seem to be part of a group, please join a group to access full functionality.', 'danger')
            return render_template('account.html', group=None, average_quiz_score=None, quizzes_completed=None)

        average_quiz_score, quizzes_completed = get_student_average_quiz_score(current_user.id)
        return render_template('account.html', group=group, teacher=teacher, students=students,
                               average_quiz_score=int(average_quiz_score), quizzes_completed=quizzes_completed,
                               group_average_quiz_score=int(group_average_quiz_score))

    if current_user.role == 'teacher':
        group_average_quiz_score = 0
        groups = Group.query.filter_by(teacher_id=current_user.id).all()
        students = 0
        for group in groups:
            students += len(Student.query.filter_by(group_id=group.id).all())
            group_average_quiz_score = get_group_average_quiz_score(group.id)
        return render_template('account.html', groups=groups, teacher=current_user, students=students,
                               group_average_quiz_score=group_average_quiz_score)

    return render_template('account.html')


@users.route('/account/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        # Gets the user
        user = User.query.filter_by(username=form.username.data).first()
        inputpass = re.compile(r'(?=.*[A-Z])(?=.*[*?!()^+%&/$#@<>=}{~£])(?=.*\d)')
        if not user or not check_password_hash(user.password, form.current_password.data):
            flash("Incorrect user or password. Please try again.", "danger")
            return render_template('auth/change_password.html', form=form)

        elif not inputpass.match(form.new_password.data):
            flash("Password requires at least 1 digit, 1 uppercase letter and 1 special character.", 'danger')

        elif str(form.new_password.data) != str(form.confirm_new_password.data):
            flash("New passwords must match.", "danger")
            return render_template('auth/change_password.html', form=form)

        # If user did enter correct current password, go ahead with password change:
        else:
            user.password = generate_password_hash(form.new_password.data)
            db.session.commit()

            flash("Your password has been changed", "info")
            logout_user()
            current_time = datetime.now().strftime("%H:%M:%S")
            body = f"""\
                        <p><b>Hello {user.name}. </b></p>
                        <br>
                        <br>
                        <p> Your password was recently changed.
                        <br>
                        <p> Time of change: {current_time}
                        <br>
                        <p>If this was not done by use, please change your website password immediately.</p>
                    """
            send_email(user, body)
            return redirect(url_for('auth.login', form=LoginForm()))
        # Checks if user entered correct current password

    return render_template('auth/change_password.html', form=form)


@users.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    form = ForgottenPassword()
    if form.validate_on_submit():
        # Gets the user
        user = User.query.filter_by(username=form.username.data).first()
        # Checks if user entered correct current password
        if not user:
            flash("That user does not exist.", "danger")
            return render_template('auth/forgotten_password.html', form=form)

        new_pass = ""
        # Auto generates new password
        nums = str(randint(1111, 9999))
        for _ in range(3):
            new_pass += words[randint(0, len(words) - 1)].replace("\n", "")
        new_pass += nums
        # Generates hash for new password and commits to the DB
        user.password = generate_password_hash(new_pass)
        db.session.commit()
        body = f"""\
                <p><b>Hello {user.name}. Your new password is {new_pass}</b></p>
                <br>
                <br>
                <p>We urge you to change the password as soon as possible.</p>
            """
        send_email(user, body)

        flash("Your new temporary password has been sent to your email.", "info")
        return redirect(url_for('auth.login', form=LoginForm()))
    return render_template('auth/forgotten_password.html', form=form)


# @users.route('/account/<string:_username>/join_group')
# @login_required
# @requires_roles('student')
# def join_group(_username):
#     return render_template('index.html')


@users.route('/content', methods=['GET'])
@login_required
def content():
    key_stage = 0
    if current_user.role == 'student':
        group_id = User.query.get(current_user.id).group_id
        group = Group.query.get(group_id)
        if group:
            key_stage = group.key_stage
    return render_template('content.html', key_stage=int(key_stage))


# Displays all the quizzes available to the current user
@users.route('/quizzes', methods=['GET', 'POST'])
@login_required
def quizzes():
    # displays all the quizzes available to the user, that is, quizzes under the same key stage as the user's group
    quizzes = []
    if current_user.role == 'student':
        for s, q, g in db.session.query(Student, Quiz, Group).filter(Student.id == current_user.id,
                                                                     Group.id == Student.group_id,
                                                                     Quiz.key_stage == Group.key_stage).all():
            quizzes.append(q)
    else:
        quizzes = Quiz.query.all()

    return render_template('quizzes/quizzes.html', current_user=current_user, quizzes=quizzes)


@users.route('/quiz_questions/<int:quiz_id>', methods=['POST', 'GET'])
@login_required
def quiz_questions(quiz_id):
    # Example
    # question = "Which of these is a Fish?"
    # choices = "Dog|Cat|Fish|Wolf|Bear"
    # correct_choice = 2

    # get all questions for the specified quiz
    quiz = Quiz.query.get(quiz_id)
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

        # saves student's quiz score to database
        quiz_score = StudentQuizScores(quiz_id=quiz_id, student_id=current_user.id, score=score)
        db.session.add(quiz_score)
        db.session.commit()

        return render_template('quizzes/quiz_results.html', quiz_score=score, quiz=quiz)
    return render_template('quizzes/quiz_question.html', form=form, quiz=quiz)


# returns the average score and number of quizzes completed by the specified student
def get_student_average_quiz_score(student_id):
    student_quiz_scores = StudentQuizScores.query.filter_by(student_id=student_id).all()

    num_of_quizzes = len(student_quiz_scores)
    if num_of_quizzes == 0:
        return 0, 0
    else:
        sum_of_all_scores = 0
        for quiz_score in student_quiz_scores:
            sum_of_all_scores += quiz_score.score

        return sum_of_all_scores / num_of_quizzes, num_of_quizzes


# returns the average score of quizzes completed specified group
def get_group_average_quiz_score(group_id):
    sum_of_all_scores = 0
    num_of_scores = 0

    for sqs, s in db.session.query(StudentQuizScores, Student).filter(
            Student.group_id == group_id,
            StudentQuizScores.student_id == Student.id).all():
        sum_of_all_scores += sqs.score
        num_of_scores += 1

    if num_of_scores == 0:
        return 0
    else:
        return int(sum_of_all_scores / num_of_scores)


def send_email(user, body):
    if user.role == 'student':
        group = Group.query.get(user.group_id)
        if group:
            email = Teacher.query.get(group.teacher_id).email
        else:
            flash('You do not seem to have a teacher, please join a group to access email functionality.', 'danger')
            return
    else:
        email = user.email

    html = f"""\
            <html>
              <head></head>
              <body>
                {body}
              </body>
              <br>
              <footer style="position:center">
              <b>Climate4Kids
              <br>
              <br>
              <i>For a better education to the next generation</i>
              </b>
              </footer>
            </html>
            """

    message = MIMEMultipart()
    message["Subject"] = f"{user.name} password reset"
    message["From"] = SMTP_EMAIL
    message["To"] = email
    message.attach(MIMEText(html, "html"))
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login(SMTP_EMAIL, SMTP_PASSWORD)
    smtp_server.sendmail(SMTP_EMAIL, email, message.as_string())
    smtp_server.close()

    logging.warning('SECURITY - reset password e-mail sent [%s, %s, %s]', current_user.id, current_user.username,
                    request.remote_addr)


"""  
Useful explanation of querying with Inheritance: https://docs.sqlalchemy.org/en/14/orm/inheritance_loading.html
"""
