from .. import db
class UserActivityPreference(db.Model):
    __tablename__ = 'user_activity_preferences'
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), primary_key=True)
    priority    = db.Column(db.Integer, default=1)

    user     = db.relationship('User',     back_populates='activity_preferences')
    activity = db.relationship('Activity', back_populates='user_activities')