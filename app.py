from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/educationalContent')
def educationalContent():
    return render_template("educationalContent.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# error pages
@app.errorhandler(400)
def page_forbidden(error):
    return render_template('errors/400.html'), 400


@app.errorhandler(403)
def page_not_found(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(503)
def internal_error(error):
    return render_template('errors/503.html'), 503


if __name__ == '__main__':
    app.run(debug=True)
