from .. import db
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    budget             = db.Column(db.Numeric)
    climate_pref       = db.Column(db.String(50))
    passport_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))

    user = db.relationship('User', back_populates='preferences')
    passport_country = db.relationship('Country')

    def __init__(self, user_id, budget, climate_pref, passport_country_id):
        self.user_id = user_id
        self.budget = budget
        self.climate_pref = climate_pref
        self.passport_country_id = passport_country_id
        