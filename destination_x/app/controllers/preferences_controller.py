""" Preferences Controller 
for handling user preferences. """
__author__ = "Akele Benjamin(620130803)"

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date

from app.models.categories import Category
from app.models.user import User
from .. import db
from app.models.user_preference import UserPreference
from flask import session, flash, redirect, url_for, request, render_template
from app.models.amenity import Amenity
from app.models.user_amenity_preference import UserAmenityPreference
from app.models.user_activity_preferences import UserActivityPreference
from app.models.activity import Activity

pref_bp = Blueprint('preferences', __name__, url_prefix='/preferences')

# Define the list of weight fields + labels for template
WEIGHT_FIELDS = [
    ('weight_winter_sports', 'Winter Sports'),
    ('weight_advennture',    'Adventure'),
    ('weight_outdoor',       'Outdoor'),
    ('weight_shopping',      'Shopping'),
    ('weight_arts',          'Arts'),
    ('weight_road',          'Road Trips'),
    ('weight_wildlife',      'Wildlife'),
    ('weight_historical',    'Historical'),
    ('weight_beach',         'Beach'),
    ('weight_food',          'Food'),
    ('weight_wine',          'Wine'),
    ('weight_education',     'Education'),
    ('weight_culture',       'Culture'),
    ('weight_wellness',      'Wellness'),
    ('weight_family',        'Family'),
    ('weight_music',         'Music'),
    ('weight_festival',      'Festival'),
    ('weight_landmarks',     'Landmarks')
]

@pref_bp.route('/', methods=['GET', 'POST'])
def preferences():
    # Require login
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    # Load or create preferences row
    pref = UserPreference.query.get(user_id)
    if not pref:
        pref = UserPreference(user_id=user_id)
        db.session.add(pref)
        db.session.commit()

    if request.method == 'POST':
        # Basic fields
        pref.budget               = float(request.form.get('budget', 0))
        pref.visa_required_filter = bool(request.form.get('visa_required_filter'))
        # Dates
        pref.check_in_date    = date.fromisoformat(request.form['check_in_date'])
        pref.check_out_date   = date.fromisoformat(request.form['check_out_date'])
        pref.number_of_travelers = int(request.form.get('number_of_travelers', 1))
        pref.weight_advennture       = float(request.form.get('weight_advennture', 0))
        pref.weight_outdoor     = float(request.form.get('weight_outdoor', 0))
        pref.weight_shopping   = float(request.form.get('weight_shopping', 0))
        pref.weight_arts     = float(request.form.get('weight_arts', 0))
        pref.weight_road       = float(request.form.get('weight_road', 0))
        pref.weight_wildlife   = float(request.form.get('weight_wildlife', 0))
        pref.weight_historical    = float(request.form.get('weight_historical', 0))
        pref.weight_beach    = float(request.form.get('weight_beach', 0))
        pref.weight_food      = float(request.form.get('weight_food', 0))
        pref.weight_wine     = float(request.form.get('weight_wine', 0))
        pref.weight_education      = float(request.form.get('weight_education', 0))
        pref.weight_culture      = float(request.form.get('weight_culture', 0))
        pref.weight_wellness   = float(request.form.get('weight_wellness', 0))
        pref.weight_family = float(request.form.get('weight_family', 0))
        pref.weight_music = float(request.form.get('weight_music', 0))
        pref.weight_festival = float(request.form.get('weight_festival', 0))
        pref.weight_landmarks      = float(request.form.get('weight_landmarks', 0))

        

        db.session.commit()
        flash('Preferences saved successfully.', 'success')
        return redirect(url_for('preferences.interests'))
    weight_values = {
        field: (getattr(pref, field) or 0)
        for field, _ in WEIGHT_FIELDS
    }

    return render_template(
        'preferences.html',
        pref=pref,
        weight_fields=WEIGHT_FIELDS,
        weight_values=weight_values
    )

@pref_bp.route('/interests', methods=['GET', 'POST'])
def interests():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))
    user = User.query.get(user_id)

    amenities = Amenity.query.order_by(Amenity.name).all()
    


    if request.method == 'POST':
        # Selected amenity IDs
        selected_amenities = request.form.getlist('amenities')
        # Clear existing
        UserAmenityPreference.query.filter_by(user_id=user_id).delete()
        for aid in selected_amenities:
            pref = UserAmenityPreference(
                user_id=user_id,
                amenity_id=int(aid),
                priority=1
            )
            db.session.add(pref)

        # Selected activity IDs
        selected_amentities = request.form.getlist('amentities')
        UserActivityPreference.query.filter_by(user_id=user_id).delete()
        for cid in selected_amentities:
            
            pref = UserActivityPreference(
                user_id=user_id,
                category_id=int(cid),
                priority=1
            )
            db.session.add(pref)

        db.session.commit()
        flash('Your interests have been saved!', 'success')
        return redirect(url_for('destinations.list_destinations'))

    # Preselected IDs for rendering
    user_amen_ids = [p.amenity_id for p in user.amenity_preferences]

    return render_template(
        'preferences_interests.html',
        amenities=amenities,
        user_amen_ids=user_amen_ids
    )