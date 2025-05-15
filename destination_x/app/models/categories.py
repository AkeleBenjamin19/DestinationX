""" Categories model """

__author__ = "Akele Benjamin(620130803)"
from .. import db
class Category(db.Model):
    __tablename__ = 'categories'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

def __init__(self, name):
    self.name = name   
