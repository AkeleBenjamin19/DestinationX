""" Home Controller """

__author__ = "Akele Benjamin(620130803)"

from flask import Blueprint, render_template
from ..models import User

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    users = User.query.all()
    return render_template('home.html', users=users)
