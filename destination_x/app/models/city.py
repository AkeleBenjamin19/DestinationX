from .. import db
class City(db.Model):
    __tablename__ = 'cities'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(128), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    latitude  = db.Column(db.Numeric(9,6))
    longitude = db.Column(db.Numeric(9,6))
    img= db.Column(db.String(255))

    country = db.relationship('Country', back_populates='cities')
    airports = db.relationship('Airport', back_populates='city')
    activities = db.relationship('Activity', back_populates='city')
    flight_origins = db.relationship(
        'FlightPrice', foreign_keys='FlightPrice.origin_city_id', back_populates='origin_city'
    )
    flight_destinations = db.relationship(
        'FlightPrice', foreign_keys='FlightPrice.destination_city_id', back_populates='destination_city'
    )
    hotels = db.relationship('Hotel', back_populates='city')
    recommendations = db.relationship('Recommendation', back_populates='city')
    destinations    = db.relationship('Destination',    back_populates='city')

    def __init__(self, name, country_id, latitude, longitude, img):
        self.name = name
        self.country_id = country_id
        self.latitude = latitude
        self.longitude = longitude
        self.img = img

        