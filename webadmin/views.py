"""
Author: Harry Hamilton
Date: 08/12/21
"""
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
import logging

from flask_login import login_required, login_user, current_user, logout_user

from werkzeug.security import check_password_hash

from app import db
from models import User
from users.forms import RegisterForm, LoginForm

webadmin_blueprint = Blueprint('webadmin', __name__, template_folder='templates')



@webadmin_blueprint.route("/register", methods = ["GET","POST",])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(username=form.username.data).first()

        # if a user is found redirect user back to signup page so user can try again
        if user:
            flash('Username address already exists')
            return render_template('webadmin.html', form=form)

        # create a new user with the form data
        new_user = User(username=form.username.data,
                        password=form.password.data,
                        last_login=form.last_login.data,
                        name = form.name.data,
                        role = form.role.data,
                        registered_on=form.registered_on.data)


        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logging.warning('SECURITY - User registration [%s, %s]', form.username.data, request.remote_addr)

        return redirect(url_for('users.login'))

    return render_template("webadmin.html")


@webadmin_blueprint.route('/login', methods = ["GET","POST",])
def login():
    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is 3 or more create an error messagemethods = ["GET","POST",]
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    form = LoginForm()

    if form.validate_on_submit():

        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(username=form.username.data).first()

        if not user or not check_password_hash(user.password, form.password.data):

            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')

            return render_template('webadmin.html', form=form)

        else:

            # if user is verified reset login attempts to 0
            session['logins'] = 0

            login_user(user)

            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.commit()

            logging.warning('SECURITY - Log in [%s, %s, %s]', user.id, user.username,
                            request.remote_addr)

            return render_template('webadmin.html', form=form)

    return render_template('webadmin.html', form=form)


@webadmin_blueprint.route('/logout', methods = ["GET","POST",])
@login_required
def logout():
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.username, request.remote_addr)

    logout_user()
    return redirect(url_for('index'))


@webadmin_blueprint.route('/logs', methods=['GET'])
def logs():
    with open("security.txt", "r") as f:
        entries = f.read().splitlines()[-25:]
        entries.reverse()

    return render_template('webadmin.html', logs=entries)
