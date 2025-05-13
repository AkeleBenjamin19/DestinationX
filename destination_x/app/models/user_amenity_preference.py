from .. import db
class UserAmenityPreference(db.Model):
    __tablename__ = 'user_amenity_preferences'
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),    primary_key=True)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
    priority   = db.Column(db.Integer, default=1)

    user    = db.relationship('User',    back_populates='amenity_preferences')
    amenity = db.relationship('Amenity', back_populates='user_preferences')

    def __init__(self, user_id, amenity_id, priority):
        self.user_id = user_id
        self.amenity_id = amenity_id
        self.priority = priority