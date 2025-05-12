from app import db
class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    cost = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    f_cost = db.Column(db.Integer)
    h_cost = db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    city = db.relationship('City', backref='activities')

    def __init__(self, name, weight_value, cost, flight_cost, hotel_cost, city_id):
        self.name = name
        self.cost = cost
        self.weight = weight_value
        self.f_cost = flight_cost
        self.h_cost = hotel_cost
        self.city_id = city_id

    def _getName(self):
        return self.name
    
    def _getWeight(self):
        return self.weight
    
    def _getCost(self):
        return self.cost
    
    def _getFlightCost(self):
        return self.f_cost
    
    def _getHotelCost(self):
        return self.h_cost
    
    def _getId(self):
        return self.id
    

        

