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

    def __init__(self, indent, air_type, name, iata_code, city_id, latitutde, longitude, iso_country, iso_region):
        self.ident = indent
        self.type = air_type
        self.name = name
        self.iata_code = iata_code
        self.city_id = city_id
        self.latitude = latitutde
        self.longitude = longitude
        self.iso_country = iso_country
        self.iso_region = iso_region