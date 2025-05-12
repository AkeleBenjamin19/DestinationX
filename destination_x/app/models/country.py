from app import db
class Country(db.Model):

    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    def __init__(self, name):
        self.name = name

    def _getName(self):
        return self.name
    

    def _getId(self):
        return self.id