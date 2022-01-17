from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, session, url_for
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy

import logging

# app configuration
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config.from_object('config.DevelopmentConfig')

# create database instance
db = SQLAlchemy(app)
print(db)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True


@app.route('/')
def index():
    return render_template("index.html")


# error pages
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
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.refresh_view = 'users.login'
    login_manager.login_message_category = 'danger'
    login_manager.login_message = 'Session timed out, please login again.'

    # login_manager.refresh_view = 'users.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # import blueprints
    from users.views import users
    from webadmin.views import webadmin_blueprint
   
    # register blueprints
    app.register_blueprint(users)
    app.register_blueprint(webadmin_blueprint)
    
    app.run(debug=True)
