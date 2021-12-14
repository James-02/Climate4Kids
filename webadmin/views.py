"""
Author: Harry Hamilton
Date: 08/12/21
"""
from flask import Blueprint, render_template
import logging

# CONFIG
webadmin_blueprint = Blueprint('webadmin', __name__, template_folder='templates')


@webadmin_blueprint.route("/webadmin")
def webadmin():
    return render_template("webadmin.html")


# Previous 25 log entries
#@webadmin_blueprint.route('/logs', methods=['POST'])
#def logs():
#    with open("\Stage2-Team-Project\security.txt", "r") as f:
#        enteries = f.read().splitlines()[-25:]
#        enteries.reverse()
#
 #   return render_template('webadmin.html', logs=enteries)
