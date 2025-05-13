from datetime import datetime
from .. import db
from .amenity import Amenity

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(128), unique=True, nullable=False)
    name       = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    # Convenience many-to-many via join table
    amenities = db.relationship(
        'Amenity', secondary='user_amenity_preferences', back_populates='users'
    )

    # Other relationships
    recommendations = db.relationship('Recommendation', back_populates='user')
    destinations    = db.relationship('Destination',    back_populates='user')

    def __init__(self, email, name):
        self.email = email
        self.name = name

    def __repr__(self):
        return f'<User {self.email}>'