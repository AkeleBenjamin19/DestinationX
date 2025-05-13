# Author: Akele Benjamin
from .. import db
class Activity(db.Model):
    __tablename__ = 'activities'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(128), nullable=False)
    category   = db.Column(db.String(64))
    city_id    = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    latitude   = db.Column(db.Numeric(9,6))
    longitude  = db.Column(db.Numeric(9,6))
    price      = db.Column(db.Float)

    city            = db.relationship('City', back_populates='activities')
    destinations    = db.relationship('Destination', back_populates='activity')
    recommendations = db.relationship('Recommendation', back_populates='activity')
    user_activities = db.relationship('UserActivityPreference', back_populates='activity')

    def __init__(self, name:str, category:str, city_id:int,  latitude, longitude, price:float):
        self.name = name
        self.category = category
        self.city_id = city_id
        self.latitude = latitude
        self.longitude = longitude
        self.price = price
        