from .. import db

# Many-to-many for hotels ⟷ amenities
hotel_amenities = db.Table(
    'hotel_amenities',
    db.Column('hotel_id', db.Integer, db.ForeignKey('hotels.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)