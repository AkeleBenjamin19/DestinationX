# Author: Akele Benjamin
from datetime import datetime
from .. import db
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