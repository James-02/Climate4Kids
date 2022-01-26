#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, session
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging


db = SQLAlchemy()

# app configuration
app = Flask(__name__, static_url_path='/static', static_folder='static')
if app.config['ENV'] == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')


# logging
def setup_logging(filename):
    """ Function to setup a logging file for important actions using logging module."""
    fh = logging.FileHandler(filename, "w")
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%m:%S %p')
    fh.setFormatter(formatter)
    logger = logging.getLogger('')
    logger.propagate = False
    logger.addHandler(fh)


def setup_login():
    """ Function to initialize the flask-login LoginManager and attributes"""
    # Flask LoginManager instance attributes
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.refresh_view = 'auth.login'
    login_manager.login_message_category = 'danger'
    login_manager.login_message = 'Session timed out, please login again.'
    login_manager.init_app(app)

    from models import User
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


@app.before_first_request
def execute_this():
    setup_logging('security.log')
    setup_login()

    # import blueprints
    from auth.views import auth
    from users.views import users
    from groups.views import groups
    from webadmin.views import webadmin_blueprint

    # register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(groups)
    app.register_blueprint(webadmin_blueprint)


@app.before_request
def before_request():
    """ A function to set the permanent session lifetime to 30 minutes before every request
    """
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True


@app.route('/')
def index():
    return render_template("index.html")


# error pages to render upon error handling
@app.errorhandler(400)
def bad_request(_error):
    return render_template('errors/400.html'), 400


@app.errorhandler(403)
def page_forbidden(_error):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def page_not_found(_error):
    return render_template('errors/404.html'), 404


@app.errorhandler(410)
def page_forbidden(_error):
    return render_template('errors/410.html'), 410


@app.errorhandler(500)
def internal_error(_error):
    return render_template('errors/500.html'), 500


@app.errorhandler(503)
def page_forbidden(_error):
    return render_template('errors/503.html'), 503


def requires_roles(*roles):
    """ Function using wraps annotation to check if the current_user has the role required."""

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # Redirect the user to an unauthorised notice!
                return render_template('errors/403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


if __name__ == '__main__':
    app.run(debug=True)
