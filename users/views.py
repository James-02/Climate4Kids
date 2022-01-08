# IMPORT
import csv
import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import flash, current_app
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from models import User, Student, Group, Teacher
from forms import CreateGroup, RegisterStudent
from random import randint

from app import app
from app import db

TEACHER_ID = 1
SMTP_EMAIL = app.config['SMTP_EMAIL']
SMTP_PASSWORD = app.config['SMTP_PASSWORD']

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
    teacher_id = TEACHER_ID # TODO replace with current_user when ready
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


@users.route('/groups/<string:group_id>/delete_group', methods=['GET'])
def delete_group(group_id):
    db.session.query(Group).filter_by(id=group_id).delete()
    db.session.commit()
    return redirect(url_for('users.dashboard'))


@users.route('/groups/<string:group_id>/edit_group', methods=['GET', 'POST'])
def edit_group(group_id):
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
            group = Group(id=str(group_id), name=str(form.name.data), size=form.size.data,
                          key_stage=form.key_stage.data, teacher_id=TEACHER_ID)
            group.teacher_id = TEACHER_ID  # TODO: Replace this test ID with current_user
            db.session.add(group)
            db.session.commit()
            return redirect(url_for('users.create_students', group_id=group_id))
    return render_template('groups/create_group.html', form=form)


@users.route('/groups/<string:group_id>/create_students', methods=['GET', 'POST'])
def create_students(group_id):
    form = RegisterStudent()
    teacher = Teacher.query.get(TEACHER_ID)
    if form.validate_on_submit():
        names = list(filter(None, (form.names.data.strip().split("\r\n"))))
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        group = Group.query.get(group_id)
        students = int(Student.query.filter_by(group_id=group_id).count())
        if students + len(names) > group.size:
            flash("Too many students for this group size, please consider increasing group size.", "danger")
            return render_template('groups/create_students.html', form=form, group_id=group_id)

        filename = f'{group.name}.csv'
        with open(filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['username', 'password'])
            writer.writeheader()

            for name in names:
                username, password = generate_account(name)
                student = Student(user_type="student", name=name, username=username, password=password,
                                  last_login=None, registered_on=date, group_id=group_id)
                db.session.add(student)
                db.session.commit()
                writer.writerow({'username': username, 'password': password})

        if not send_student_data(group.name, filename, teacher.email):
            flash(f"Unable to send CSV to {teacher.email}, please contact an admin for help.", "danger")
        else:
            return redirect(url_for('users.group', group_id=group_id))

    return render_template('groups/create_students.html', form=form, group_id=group_id)


@users.route('/groups/<string:group_id>/', methods=['GET'])
def download_students(group_id):
    """ Method to be able to download student data, currently downloads 'name' and 'last_login',
    could be expanded further to download quiz data when the feature is available."""
    group = Group.query.get(group_id)
    filename = f'{group.name}.csv'
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'last_login'])
        writer.writeheader()

        for student in Student.query.filter_by(group_id=group_id):
            writer.writerow({'username': student.username, 'last_login': student.last_login})

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

