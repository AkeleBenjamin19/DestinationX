# Author: Akele Benjamin
from .. import db
class Airport(db.Model):
    __tablename__ = 'airports'
    id         = db.Column(db.Integer, primary_key=True)
    ident      = db.Column(db.String(50), unique=True)
    type       = db.Column(db.String(50))
    name       = db.Column(db.String(255), nullable=False)
    iata_code  = db.Column(db.String(3))
    city_id    = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    latitude   = db.Column(db.Numeric(9,6))
    longitude  = db.Column(db.Numeric(9,6))
    iso_country = db.Column(db.String(2))
    iso_region  = db.Column(db.String(50))

    city = db.relationship('City', back_populates='airports')