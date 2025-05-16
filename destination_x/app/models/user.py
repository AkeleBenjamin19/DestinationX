# Author: Akele Benjamin
from datetime import datetime
from .. import db
from .amenity import Amenity

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(128), unique=True, nullable=False)
    name       = db.Column(db.String(64))
    password_hash    = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_birth = db.Column(db.Date)
    port_of_origin = db.Column(db.String(64))
    country_residence = db.Column(db.String(64))

    # One-to-one user preference
    preferences = db.relationship(
        'UserPreference', back_populates='user', uselist=False
    )

    # Association-object relationships
    activity_preferences = db.relationship(
        'UserActivityPreference', back_populates='user', cascade='all, delete-orphan'
    )
    amenity_preferences = db.relationship(
        'UserAmenityPreference', back_populates='user', cascade='all, delete-orphan'
    )

    
    amenities = db.relationship(
        'Amenity', secondary='user_amenity_preferences', back_populates='users'
    )

    
    recommendations = db.relationship('Recommendation', back_populates='user')
    destinations    = db.relationship('Destination',    back_populates='user')

    def __repr__(self):
        return f'<User {self.email}>'