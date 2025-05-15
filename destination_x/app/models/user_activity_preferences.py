""" User Activity Preference Model """

__author__ = "Akele Benjamin(620130803)"
from .. import db
class UserActivityPreference(db.Model):
    __tablename__ = 'user_activity_preferences'
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)
    priority    = db.Column(db.Integer, default=1)

    user     = db.relationship('User',     back_populates='activity_preferences')

    def __init__(self, user_id, category_id, priority):
        self.user_id = user_id
        self.category_id = category_id
        self.priority = priority
        