""" This controller handles user authentication, including login and signup.
It also handles user preferences and other related functionalities.
"""

__author__ = "Akele Benjamin(620130803)"
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.airport import Airport
from app.models.country import Country

# Auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        # Set the user in session
        session['user_id'] = user.id 
        print(f"User ID: {user.id}")
        flash('Logged in successfully', 'success')
        return redirect(url_for('preferences.preferences'))
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # Load dropdown data
    airports = Airport.query.order_by(Airport.name).all()
    # Countries associated with those airports
    country_ids = set(a.city.country_id for a in airports if a.city)
    countries = Country.query.filter(Country.id.in_(country_ids)).order_by(Country.name).all()

    if request.method == 'POST':
        name       = request.form.get('name')
        email      = request.form.get('email')
        password   = request.form.get('password')
        confirm    = request.form.get('confirm')
        airport = request.form.get('airport_id')
        country = request.form.get('country_id')

        # validation
        if not (name and email and password and airport and country):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.signup'))
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.signup'))

        # create user
        user = User(name=name, email=email, password_hash=generate_password_hash(password))

        airport_id= Airport.query.filter_by(name=airport).first()

        country_id = Country.query.filter_by(name=country).first()
       
       #Fetch airport and country IDs from the database
        airport_id = Airport.query.filter_by(id=airport).first()
        airport_name = airport_id.name
        country_id = Country.query.filter_by(id=country).first()
        country_name = country_id.name

        user = User(name=name, email=email, password_hash=generate_password_hash(password),port_of_origin=airport_name,country_residence=country_name) 
        # user.origin_airport_id = airport_name
        # user.passport_country_id = country_name
        db.session.add(user)
        db.session.flush()  # to assign user.id

        # create preferences row

        db.session.commit()

        # Set user in session
        session['user_id'] = user.id 
        print(f"User ID: {user.id}")
        flash('Account created! Please set your preferences.', 'success')
        return redirect(url_for('preferences.preferences'))

    return render_template(
        'auth/signup.html',
        airports=airports,
        countries=countries
    )
