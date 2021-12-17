from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from users.views import users
import logging


# app configuration
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# create database instance
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
    # Imports blueprints
    from webadmin.views import webadmin_blueprint
    app.register_blueprint(webadmin_blueprint)

    app.run(debug=True)


