""" Country model """
__author__ = "Akele Benjamin(620130803)"
from .. import db
class Country(db.Model):
    __tablename__ = 'countries'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(128), unique=True, nullable=False)
    demonym        = db.Column(db.String(64))
    iso_code       = db.Column(db.String(2), unique=True, nullable=False)
    continent      = db.Column(db.String(64))
    continent_code = db.Column(db.String(2))

    cities          = db.relationship('City',       back_populates='country')
    visa_origins    = db.relationship(
        'VisaPolicy', foreign_keys='VisaPolicy.origin_id', back_populates='origin_country'
    )
    visa_destinations = db.relationship(
        'VisaPolicy', foreign_keys='VisaPolicy.destination_id', back_populates='destination_country'
    )
    destinations    = db.relationship('Destination', back_populates='country')
    recommendations = db.relationship('Recommendation', back_populates='country')

    def __init__(self, name:str, demonym:str, iso_code:str, continent:str, continent_code:str):
        self.name = name
        self.demonym = demonym
        self.iso_code = iso_code
        self.continent = continent
        self.continent_code = continent_code