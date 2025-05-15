""" Destination model """
__author__ = "Akele Benjamin(620130803)"
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

    def __init__(self, user_id, country_id, city_id, hotel_id, activity_id):
        self.user_id = user_id
        self.country_id = country_id
        self.city_id = city_id
        self.hotel_id = hotel_id
        self.activity_id = activity_id
        