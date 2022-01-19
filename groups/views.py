
# IMPORT
import csv
import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint

from flask import flash, current_app, Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required

from users.views import users, get_student_average_quiz_score
from app import db, app, requires_roles
from groups.forms import CreateGroup, RegisterStudent
from models import User, Student, Group, Teacher

import logging

# CONFIG
SMTP_EMAIL = app.config['SMTP_EMAIL']
SMTP_PASSWORD = app.config['SMTP_PASSWORD']
groups = Blueprint('groups', __name__, template_folder='templates')

# Read Dictionary
# REFERENCE: https://eslgrammar.org/list-of-nouns/#List_of_Nouns_in_English
with open("static/dict.txt", "r") as r:
    words = r.readlines()


@groups.route('/groups/<string:group_id>', methods=['GET'])
@login_required
@requires_roles('teacher')
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


@groups.route('/groups/create_group', methods=['GET', 'POST'])
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

            logging.warning('SECURITY - Created Group [%s, %s, %s, %s]',group_id, current_user.id,
                            current_user.username, request.remote_addr)

            return redirect(url_for('groups.create_students', group_id=group_id))
    return render_template('groups/create_group.html', form=form)


@groups.route('/groups/<string:group_id>/create_students', methods=['GET', 'POST'])
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
            logging.warning('SECURITY - Created Students [%s, %s, %s, %s]',group_id , current_user.id,
                            current_user.username,request.remote_addr)

            return redirect(url_for('groups.group', group_id=group_id))

    return render_template('groups/create_students.html', form=form, group_id=group_id)


@groups.route('/groups/<string:group_id>/delete_group', methods=['GET'])
@login_required
@requires_roles('teacher')
def delete_group(group_id):
    db.session.query(Group).filter_by(id=group_id).delete()
    db.session.commit()

    logging.warning('SECURITY - Deleted Group [%s, %s, %s, %s]',group_id, current_user.id, current_user.username,
                    request.remote_addr)

    return redirect(url_for('users.dashboard'))


@groups.route('/groups/<string:group_id>/edit_group', methods=['GET', 'POST'])
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
        return redirect(url_for('groups.group', group_id=group_id))
    return render_template('groups/edit_group.html', form=form, group_id=group_id, group=group)


@groups.route('/groups/<string:group_id>/', methods=['GET'])
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
