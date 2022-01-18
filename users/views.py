
# IMPORT
import csv
import logging
import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime
from flask import flash, current_app, Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Student, Group, Teacher
from users.forms import CreateGroup, RegisterStudent, LoginForm, ChangePassword
from flask import flash, current_app, Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_user, current_user, login_required, logout_user
from flask_navigation import Navigation
from wtforms.fields.core import Label
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, Student, Group, Teacher, Quiz, Question, StudentQuizScores
from users.forms import CreateGroup, RegisterStudent, LoginForm, QuizForm, ChangePassword, ForgottenPassword

from random import randint
from app import db, app, requires_roles

# CONFIG
SMTP_EMAIL = app.config['SMTP_EMAIL']
SMTP_PASSWORD = app.config['SMTP_PASSWORD']
users = Blueprint('users', __name__, template_folder='templates')

# Read Dictionary
# REFERENCE: https://eslgrammar.org/list-of-nouns/#List_of_Nouns_in_English
with open("static/dict.txt", "r") as r:
    words = r.readlines()


# VIEWS
@users.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')


@users.route('/login', methods=['GET', 'POST'])
def login():
    """
    Allows for users to login to the web application.
    """
    # create login attribute if it doesnt exist
    if not session.get('logins'):
        session['logins'] = 0
    # display error if user has made 4+ invalid login attempts
    elif session.get('logins') > 3:
        flash('Exceeded 3 login attempts', "danger")

    # create login form object
    form = LoginForm()

    if form.validate_on_submit():
        # increment login attempt counter
        session['logins'] += 1

        # get user (if they exist) by their username
        user = User.query.filter_by(username=form.username.data).first()
        # check if user has entered valid credentials
        if not user or not check_password_hash(user.password, form.password.data):
            # flash a warning message and reload the page if credentials are invalid
            if session['logins'] > 3:
                flash("Exceeded login attempts.", "danger")
            flash('Incorrect Username or Password, please try again.', 'danger')
            return render_template('auth/login.html', form=form)

        # login the user
        if request.form.get('remember_me') == 'on':
            login_user(user, remember=True)
        else:
            login_user(user, remember=False)

        session['logins'] = 0  # reset login counter to 0 on a successful login
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        user.last_login = date
        db.session.commit()
        # redirect the user to the appropriate page for their role
        if current_user.role == 'teacher':  # this may need changing
            return redirect(url_for('users.dashboard'))
        else:
            return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


# logout user profile
@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@users.route('/dashboard', methods=['GET'])
@login_required
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
        teacher = None
        students = None
        if group is not None:
            students = len(group.students)
            teacher = Teacher.query.get(group.teacher_id)
        average_quiz_score, quizzes_completed = get_student_average_quiz_score(current_user.id)
        return render_template('account.html', group=group, teacher=teacher, students=students,
                               average_quiz_score=average_quiz_score, quizzes_completed=quizzes_completed)

    if current_user.role == 'teacher':
        groups = Group.query.filter_by(teacher_id=current_user.id).all()
        students = 0
        for group in groups:
            students += len(Student.query.filter_by(group_id=group.id).all())
        return render_template('account.html', groups=groups, teacher=current_user, students=students)

    return render_template('account.html')


@users.route('/account/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        # Gets the user
        user = User.query.filter_by(username=form.username.data).first()
        # Checks if user entered correct current password
        if not user or not check_password_hash(user.password, form.current_password.data):
            flash("Incorrect current password. Please try again.", "danger")

            return render_template('change_password.html', form=form)
        # If user did enter correct current password, go ahead with password change:
        new_pass = form.new_password.data

        new_pass = generate_password_hash(new_pass)
        # If user did enter correct current password, go ahead with password change:
        user.password = new_pass


        db.session.add(user)
        db.session.commit()

        return render_template('index.html')
    return render_template('change_password.html', form=form)


@users.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    form = ForgottenPassword()
    if form.validate_on_submit():
        print("test")
        # Gets the user
        user = User.query.filter_by(username=form.username.data).first()
        # Checks if user entered correct current password
        if not user:
            print("test3")
            flash("That account does not exist.", "danger")
            return render_template('forgotten_password.html', form=form)

        print("test4")
        new_pass = ""
        nums = str(randint(1111, 9999))
        for _ in range(3):
            new_pass += words[randint(0, len(words) - 1)].replace("\n", "")
        new_pass += nums
        print(new_pass)
        new_pass = generate_password_hash(new_pass)
        # If user did enter correct current password, go ahead with password change:
        user.password = new_pass
        print(user.password)
        db.session.add(user)
        user2 = User.query.filter_by(username=form.username.data).first()
        print(user.password)
        print(user2.password)
        db.session.commit()

        return render_template('index.html')
    print("test2")
    return render_template('forgotten_password.html', form=form)



@users.route('/account/<string:_username>/join_group')
@login_required
@requires_roles('student')
def join_group(_username):
    return render_template('index.html')


@users.route('/content', methods=['GET'])
@login_required
def content():
    return render_template('content.html')


# Displays all the quizzes available to the current user
@users.route('/quizzes', methods=['GET', 'POST'])
@login_required
@requires_roles('student')
def quizzes():
    # displays all the quizzes available to the user, that is, quizzes under the same key stage as the user's group
    available_quizzes = []
    for s, q, g in db.session.query(Student, Quiz, Group).filter(Student.id == current_user.id,
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

        return render_template('quizzes.html', current_user=current_user)


@users.route('/quiz_questions/<int:quiz_id>', methods=['POST', 'GET'])
@login_required
@requires_roles('student')
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

        # saves student's quiz score to database
        quiz_score = StudentQuizScores(quiz_id=quiz_id, student_id=current_user.id, score=score)
        db.session.add(quiz_score)
        db.session.commit()

        return render_template('quiz_results.html', quiz_score=score)

    return render_template('quiz_question.html', form=form)


@users.route('/groups/<string:group_id>', methods=['GET'])
@login_required
def group(group_id):
    group_obj = Group.query.get(group_id)
    student_list = Student.query.filter_by(group_id=group_id).all()

    students_info = []
    # for each student get their Name, Last login, how many quizzes they have completed and their average quiz score
    for student in student_list:
        average_score, num_of_quizzes = get_student_average_quiz_score(student.id)
        student_info = [student.name, student.last_login, num_of_quizzes, int(average_score)]

        students_info.append(student_info)

    return render_template('groups/group.html',
                           group=group_obj,
                           students_info=students_info)


# returns the average score and number of quizzes completed by the specified student
def get_student_average_quiz_score(student_id):
    student_quiz_scores = StudentQuizScores.query.filter_by(student_id=student_id).all()

    num_of_quizzes = len(student_quiz_scores)
    num_of_quizzes = 0
    if num_of_quizzes == 0:
        return 0, 0
    else:
        sum_of_all_scores = 0
        for quiz_score in student_quiz_scores:
            sum_of_all_scores += quiz_score.score

        return sum_of_all_scores / num_of_quizzes, num_of_quizzes


@users.route('/groups/create_group', methods=['GET', 'POST'])
@login_required
@requires_roles('teacher')
def create_group():
    form = CreateGroup()
    if form.validate_on_submit():
        group_id = randint(111111, 999999)
        id_check = Group.query.filter_by(id=group_id).first()

        # while loop to check that the ID does not already exist
        while id_check:
            group_id = randint(111111, 999999)
            id_check = Group.query.filter_by(id=group_id).first()

        else:
            group = Group(id=str(group_id), name=str(form.name.data), size=form.size.data,
                          key_stage=form.key_stage.data, teacher_id=current_user.id)
            group.teacher_id = current_user.id
            db.session.add(group)
            db.session.commit()
            return redirect(url_for('users.create_students', group_id=group_id))
    return render_template('groups/create_group.html', form=form)


@users.route('/groups/<string:group_id>/create_students', methods=['GET', 'POST'])
@login_required
@requires_roles('teacher')
def create_students(group_id):
    """Allows for teachers to create student accounts, then will send the details to the
    teachers email address.
    """
    form = RegisterStudent()
    teacher = Teacher.query.get(current_user.id)
    if form.validate_on_submit():
        # Takes the names and splits them by line
        names = list(filter(None, (form.names.data.strip().split("\r\n"))))
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Current time/date
        group = Group.query.get(group_id)
        students = int(Student.query.filter_by(group_id=group_id).count())
        # Validates that there aren't too many students
        if students + len(names) > group.size:
            flash("Too many students for this group size, please consider increasing group size.", "danger")
            return render_template('groups/create_students.html', form=form, group_id=group_id)

        # Makes file with the students name/passwords
        filename = f'{group.name}.csv'
        with open(filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['username', 'password'])
            writer.writeheader()

            # Commits these students to the database
            for name in names:
                username, password = generate_account(name)
                student = Student(role="student", name=name, username=username, password=password,
                                  last_login=None, registered_on=date, group_id=group_id)
                db.session.add(student)
                db.session.commit()
                writer.writerow({'username': username, 'password': password})

        if not send_student_data(group.name, filename, teacher.email):
            flash(f"Unable to send CSV to {teacher.email}, please contact help.Climate4kids@gmail.com", "danger")
        else:
            return redirect(url_for('users.group', group_id=group_id))

    return render_template('groups/create_students.html', form=form, group_id=group_id)


@users.route('/groups/<string:group_id>/delete_group', methods=['GET'])
@login_required
@requires_roles('teacher')
def delete_group(group_id):
    db.session.query(Group).filter_by(id=group_id).delete()
    db.session.commit()
    return redirect(url_for('users.dashboard'))


@users.route('/groups/<string:group_id>/edit_group', methods=['GET', 'POST'])
@login_required
@requires_roles('teacher')
def edit_group(group_id):
    """Allows for teachers to edit group details.
    """
    form = CreateGroup()
    group = Group.query.get(group_id)
    if form.validate_on_submit():
        values = {'name': form.name.data, 'size': form.size.data, 'key_stage': form.key_stage.data}
        students = db.session.query(Student).filter_by(group_id=group_id).all()
        if int(form.size.data) < len(students):
            flash("You must set a size greater than or equal to the number of students in this group.", "danger")
            return render_template('groups/edit_group.html', form=form, group_id=group_id, group=group)

        db.session.query(Group).filter_by(id=group_id).update(values)
        db.session.commit()
        return redirect(url_for('users.group', group_id=group_id))
    return render_template('groups/edit_group.html', form=form, group_id=group_id, group=group)


@users.route('/groups/<string:group_id>/', methods=['GET'])
@login_required
@requires_roles('teacher')
def download_students(group_id):
    """ Method to be able to download student data, currently downloads 'name' and 'last_login',
    could be expanded further to download quiz data when the feature is available."""
    group = Group.query.get(group_id)
    filename = f'{group.name}.csv'
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'last_login', 'quizzes_completed', 'avg_quiz_score'])
        writer.writeheader()

        for student in Student.query.filter_by(group_id=group_id):
            writer.writerow({'username': student.username,
                             'last_login': student.last_login,
                             'quizzes_completed': None,
                             'avg_quiz_score': None})

    def generate():
        """ Generation method using yield to allow for storage of the file in memory,
        allowing the file to be removed from the system before the data is returned. """
        with open(filename) as f:
            yield from f

        os.remove(filename)

    response = current_app.response_class(generate(), mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename=filename)
    return response


def send_student_data(group_name, filename, teacher_email):
    """ Function to send the user an email containing a CSV file of the student data."""
    message = MIMEMultipart()
    message["Subject"] = f"{group_name} Accounts"
    message["From"] = SMTP_EMAIL
    message["To"] = teacher_email

    html = f"""\
    <html>
      <head></head>
      <body>
        <p><b>Your student accounts created for {group_name}.</b></p>
        <br>
        <br>
        <p>We urge you to change these passwords as soon as possible.</p>
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
    message.attach(MIMEText(html, "html"))

    with open(filename, "rb") as a:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(a.read())
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    message.attach(attachment)
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp_server.sendmail(SMTP_EMAIL, teacher_email, message.as_string())
        smtp_server.close()
        return True

    except Exception as e:
        print(e)  # TODO: add to logging
        return False

    finally:
        if '.csv' in filename:
            os.remove(filename)


def generate_account(name):
    """ Function to generate a username and a password of three random words and 4 random digits,
    the digits in the password will be the same as in the username.
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


"""  
Useful explanation of querying with Inheritance: https://docs.sqlalchemy.org/en/14/orm/inheritance_loading.html
"""

