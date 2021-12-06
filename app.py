from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_mysqldb import MySQL
from users.views import users
import mysql.connector as mysql

import pymysql

# APP CONFIGURATION
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='test',  # TODO: Configuration values here will later be put into a config.py
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://db_name:db_password@db_hostname:3306/db_name',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)
print(db)

# blueprint registration
app.register_blueprint(users)


@app.route('/')
def index():
    return render_template("index.html")


# error pages
@app.errorhandler(400)
def page_forbidden(_error):
    return render_template('errors/400.html'), 400


@app.errorhandler(403)
def page_not_found(_error):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def internal_error(_error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(_error):
    return render_template('errors/500.html'), 500


@app.errorhandler(503)
def internal_error(_error):
    return render_template('errors/503.html'), 503


if __name__ == '__main__':
    app.run(debug=True)


