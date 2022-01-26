# IMPORT
from flask import flash, Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import check_password_hash
from datetime import datetime
from models import db, User, Teacher
from auth.forms import RegisterForm, LoginForm

import logging

# CONFIG
auth = Blueprint('auth', __name__, template_folder='templates')


# VIEWS
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Created register form
    form = RegisterForm()

    if form.validate_on_submit():
        # Checks if the username entered already exists in the database
        user = User.query.filter_by(username=form.username.data).first()
        email = Teacher.query.filter_by(email=form.email.data).first()

        if user:
            # If the username exists, an error is flashed and the page is reloaded
            flash('Sorry, this username already exists.', 'danger')
            return render_template('auth/register.html', form=form)

        elif email:
            # If the email is being used, an error is flashed and the page is reloaded
            flash('Sorry, this email is already in use.', 'danger')
            return render_template('auth/register.html', form=form)

        elif str(form.password.data) != str(form.repeatpassword.data):
            # If the passwords are not equal, an error is flashed and the page is reloaded
            flash('Passwords must match.', 'danger')
            return render_template('auth/register.html', form=form)

        else:
            if form.email.data[-6:] == ".ac.uk" or form.email.data[-4:] == ".edu" or form.email.data[-7:] == ".sch.uk":
                # If the username doesn't already exist, an account is created with the information the user input
                teacher = Teacher(role="teacher",
                                  name=form.fullname.data,
                                  username=form.username.data,
                                  password=form.password.data,
                                  last_login=None,
                                  registered_on=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                  email=form.email.data)
                db.session.add(teacher)
                db.session.commit()

                logging.warning('SECURITY - User registration [%s, %s]', form.username.data, request.remote_addr)
                return login()
            else:
                flash("Sorry - we only accept emails ending in '.ac.uk', '.edu' or '.sch.uk'! "
                      "If you are a teacher but don't have access to one of these email domains, "
                      "please email us at 'help.Climate4kids@gmail.com'", "warning")

    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
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

        logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.username,request.remote_addr)
        # redirect the user to the appropriate page for their role
        if current_user.role == 'teacher':  # this may need changing
            return redirect(url_for('users.dashboard'))
        else:
            return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


# logout user profile
@auth.route('/logout')
@login_required
def logout():
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.username, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))
