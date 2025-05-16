# Author: Akele Benjamin
from .. import db
class UserActivityPreference(db.Model):
    __tablename__ = 'user_activity_preferences'
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)
    priority    = db.Column(db.Integer, default=1)

    user     = db.relationship('User',     back_populates='activity_preferences')