"""
Author: Harry Hamilton
Date: 08/12/21
"""
from flask import Blueprint, redirect, url_for
import logging

from flask_login import current_user
from models import Group

webadmin_blueprint = Blueprint('webadmin', __name__, template_folder='templates')

  
@webadmin_blueprint.route('/logs', methods=['POST'])
def logs():
    admin_ids = Group.query.filter(group_id == '-1').all()
    if current_user.id not in admin_ids:
        return redirect(url_for('page_forbidden'))
    else:
        with open("security.txt", "r") as f:
            entries = f.read().splitlines()[-25:]
            entries.reverse()

         