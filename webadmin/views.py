"""
Author: Harry Hamilton
Date: 08/12/21
"""
from flask import Blueprint, render_template
import logging

# CONFIG
webadmin_blueprint = Blueprint('webadmin', __name__, template_folder='templates')


@webadmin_blueprint.route('/logs', methods=['POST'])
def logs():
    admin_ids = Group.query.filter(group_id == '-1').all()

    if current_user.id not in admin_ids:
        return redirect(url_for('page_forbidden'))
    else:
        with open("C:/Users/Joppy/Documents/Programming/UniStuff/2033/Stage2-Team-Project/security.txt", "r") as f:
            entries = f.read().splitlines()[-25:]
            entries.reverse()

            return render_template('webadmin.html', logs=enteries)
