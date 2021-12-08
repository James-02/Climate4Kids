"""
Author: Harry Hamilton
Date: 08/12/21
"""
from flask import Blueprint, render_template

# CONFIG
webadmin_blueprint = Blueprint('webadmin', __name__, template_folder='templates')


@webadmin_blueprint.route("/webadmin")
def webadmin():
    return render_template("webadmin.html")

