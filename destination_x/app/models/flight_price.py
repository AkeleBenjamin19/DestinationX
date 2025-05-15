""" FlightPrice model """

__author__ = "Akele Benjamin(620130803)"
from datetime import datetime
from .. import db
from datetime import date
class FlightPrice(db.Model):
    __tablename__ = 'flight_prices'
    id                 = db.Column(db.Integer, primary_key=True)
    origin_city_id     = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    destination_city_id= db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    departure_date     = db.Column(db.Date, nullable=False)
    return_date        = db.Column(db.Date)
    adults             = db.Column(db.Integer, nullable=False)
    max_price_filter   = db.Column(db.Numeric)
    currency_code      = db.Column(db.String(3))
    best_price         = db.Column(db.Numeric)
    stops_allowed      = db.Column(db.SmallInteger)
    fetched_at         = db.Column(db.DateTime, default=datetime.utcnow)

    origin_city      = db.relationship(
        'City', foreign_keys=[origin_city_id], back_populates='flight_origins'
    )
    destination_city = db.relationship(
        'City', foreign_keys=[destination_city_id], back_populates='flight_destinations'
    )

    def __init__(self, orgin_city_id: int, destination_city_id: int, departure_date:date, return_date:date, adults:int, max_price_filter,currency_code, best_price, stops_allowed:int):
        self.origin_city_id = orgin_city_id
        self.destination_city_id = destination_city_id
        self.departure_date = departure_date
        self.return_date = return_date
        self.adults = adults
        self.max_price_filter = max_price_filter
        self.currency_code = currency_code
        self.best_price = best_price
        self.stops_allowed = stops_allowed
     
