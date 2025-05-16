# Author: Akele Benjamin
from datetime import datetime
from .. import db
class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    country_id  = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    city_id     = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    hotel_id    = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=True)
    score       = db.Column(db.Float, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    user      = db.relationship('User',       back_populates='recommendations')
    country   = db.relationship('Country',    back_populates='recommendations')
    city      = db.relationship('City',       back_populates='recommendations')
    hotel     = db.relationship('Hotel',      back_populates='recommendations')
    activity  = db.relationship('Activity',   back_populates='recommendations')