from .. import db
from .hotel_amentity import hotel_amenities
class Hotel(db.Model):
    __tablename__ = 'hotels'
    id               = db.Column(db.Integer, primary_key=True)
    external_hotel_id = db.Column(db.String(255), unique=True)
    name             = db.Column(db.String(255))
    address          = db.Column(db.Text)
    city_id          = db.Column(db.Integer, db.ForeignKey('cities.id'))
    latitude         = db.Column(db.Numeric(9,6))
    longitude        = db.Column(db.Numeric(9,6))
    distance_to_airport = db.Column(db.Integer)
    rating           = db.Column(db.Float)
    price            = db.Column(db.Float)

    city = db.relationship('City', back_populates='hotels')
    amenities = db.relationship(
        'Amenity', secondary=hotel_amenities, back_populates='hotels'
    )
    recommendations = db.relationship('Recommendation', back_populates='hotel')
    destinations    = db.relationship('Destination',    back_populates='hotel')

    def __init__(self, external_hotel_id, name, address, city_id, latitude, longitude, distance_to_airport, rating, price):
        self.external_hotel_id = external_hotel_id
        self.name = name
        self.address = address
        self.city_id  = city_id
        self.latitude = latitude
        self.longitude = longitude
        self.distance_to_airport = distance_to_airport
        self.rating = rating
        self.price = price