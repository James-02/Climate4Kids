"""
Author: Harry Hamilton
Date: 08/12/21
"""
from flask import Blueprint, render_template
from flask_login import current_user, login_required
import logging

from models import Group

# CONFIG
webadmin_blueprint = Blueprint('webadmin', __name__, template_folder='templates')


@webadmin_blueprint.route('/logs', methods=['GET'])
@login_required
def logs():
    group = Group.query.get('-1')
    if current_user.id != group.teacher_id:
        return render_template('errors/403.html')

    else:
        try:
            with open("security.log", "r") as f:
                entries = f.read().splitlines()[-25:]
                entries.reverse()
                return render_template('webadmin.html', logs=entries)
        except:
            return render_template('webadmin.html', logs=None)

