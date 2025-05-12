from  app import db
class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    country = db.relationship('Country', backref='cities')
    
    def __init__(self, name, country_id):
        self.name = name
        self.country_id = country_id

    def _getName(self):
        return self.name

    def _getCountryId(self):
        return self.country_id

    def _getId(self):
        return self.id
    
    def __repr__(self):
        return f'<City {self.name}>'


    