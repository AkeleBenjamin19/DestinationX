# Author: Akele Benjamin
from .. import db
class Destination(db.Model):
    __tablename__ = 'destinations'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    city_id    = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    hotel_id   = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=True)
    activity_id= db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=True)

    user      = db.relationship('User',      back_populates='destinations')
    country   = db.relationship('Country',   back_populates='destinations')
    city      = db.relationship('City',      back_populates='destinations')
    hotel     = db.relationship('Hotel',     back_populates='destinations')
    activity  = db.relationship('Activity',  back_populates='destinations')