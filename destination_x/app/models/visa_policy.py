# Author: Akele Benjamin
from .. import db
class VisaPolicy(db.Model):
    __tablename__ = 'visa_policies'
    origin_id      = db.Column(db.Integer, db.ForeignKey('countries.id'), primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('countries.id'), primary_key=True)
    visa_free      = db.Column(db.Boolean, default=False, nullable=False)
    without_passport= db.Column(db.Boolean, default=False, nullable=False)
    e_visa         = db.Column(db.Boolean, default=False, nullable=False)
    visa_on_arrival= db.Column(db.Boolean, default=False, nullable=False)
    visa_required  = db.Column(db.Boolean, default=False, nullable=False)

    origin_country      = db.relationship(
        'Country', foreign_keys=[origin_id], back_populates='visa_origins'
    )
    destination_country = db.relationship(
        'Country', foreign_keys=[destination_id], back_populates='visa_destinations'
    )