# Author: Akele Benjamin
# THis Table is used to create a many-to-many relationship between hotels and amenities.
from .. import db


hotel_amenities = db.Table(
    'hotel_amenities',
    db.Column('hotel_id', db.Integer, db.ForeignKey('hotels.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)