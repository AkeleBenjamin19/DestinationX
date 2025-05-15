""" User Preference Model """

__author__ = "Akele Benjamin(620130803)"
from .. import db
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    budget             = db.Column(db.Numeric)
    climate_pref       = db.Column(db.String(50))
    check_in_date      = db.Column(db.Date)
    check_out_date     = db.Column(db.Date)
    number_of_travelers = db.Column(db.Integer)
    currency_code      = db.Column(db.String(3))
    visa_required_filter       = db.Boolean
    weight_winter_sports = db.Column(db.Numeric)
    weight_advennture       = db.Column(db.Numeric)
    weight_outdoor     = db.Column(db.Numeric)
    weight_shopping   = db.Column(db.Numeric)
    weight_arts     = db.Column(db.Numeric)
    weight_road       = db.Column(db.Numeric)
    weight_wildlife   = db.Column(db.Numeric)
    weight_historical    = db.Column(db.Numeric)
    weight_beach    = db.Column(db.Numeric)
    weight_food      = db.Column(db.Numeric)
    weight_wine     = db.Column(db.Numeric)
    weight_education      = db.Column(db.Numeric)
    weight_culture      = db.Column(db.Numeric)
    weight_wellness   = db.Column(db.Numeric)
    weight_family = db.Column(db.Numeric)
    weight_music = db.Column(db.Numeric)
    weight_festival = db.Column(db.Numeric)
    weight_landmarks      = db.Column(db.Numeric)

    user = db.relationship('User', back_populates='preferences')

    def __init__(self, user_id, budget, climate_pref, check_in_date, check_out_date, number_of_travelers, currency_code, visa_required_filter, weight_winter_sports, weight_advennture, weight_outdoor, weight_shopping, weight_arts, weight_road, weight_wildlife, weight_historical, weight_beach, weight_food, weight_wine, weight_education, weight_culture, weight_wellness, weight_family, weight_music, weight_festival):
        self.user_id = user_id
        self.budget = budget
        self.climate_pref = climate_pref
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.number_of_travelers = number_of_travelers
        self.currency_code = currency_code
        self.visa_required_filter = visa_required_filter
        self.weight_winter_sports = weight_winter_sports
        self.weight_advennture = weight_advennture
        self.weight_outdoor = weight_outdoor
        self.weight_shopping = weight_shopping
        self.weight_arts = weight_arts
        self.weight_road = weight_road
        self.weight_wildlife = weight_wildlife
        self.weight_historical = weight_historical
        self.weight_beach = weight_beach
        self.weight_food = weight_food
        self.weight_wine = weight_wine
        self.weight_education = weight_education
        self.weight_culture = weight_culture
        self.weight_wellness = weight_wellness
        self.weight_family = weight_family
        self.weight_music = weight_music
        self.weight_festival = weight_festival
        