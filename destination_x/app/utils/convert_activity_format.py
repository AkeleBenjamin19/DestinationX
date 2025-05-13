from app import db
from app.models.activity import Activity
from app.models.city import City
from app.models.country import Country
from app.models.flight_price import FlightPrice
from app.models.hotel import Hotel

"""
    The function accepts two arguments. This being the activity and the weight. It converts the activity into a list 
    that makes calculations for the recommender easier.

    ARGS
    activity: the user selected activity
    weight: the user determined weight

    OUTPUT
    returns a tuple that contains the name of activity, weight, activity_cost, flight_cost and hotel_cost
    
"""
class convertActivitiesToTuple:

    def __init__(self, activity, weight):
        self.activity = activity
        self.weight = weight

    def convertActivityFormat(self) -> tuple:
        #db.session.query(City.name).join(Country, Country.id == City.country_id).filter(Country.name == country).first()
        activity_cost= db.session.execute(db.select(Activity.price).filter(Activity.name == self.activity)).scalars().one()
        flight_cost = db.session.execute(db.select(FlightPrice.best_price).join(City, FlightPrice.destination_city_id == City.id).join(Activity, Activity.city_id==City.id).filter(Activity.name == self.activity)).scalars().one()
        hotel_cost = db.session.execute(db.select(Hotel.price).join(City, Hotel.city_id== City.id).join(Activity, City.id == Activity.city_id).filter(Activity.name == self.activity)).scalars().one()
        
        flight_cost = float(flight_cost)
        activity_tuple =(self.activity, self.weight, activity_cost, flight_cost, hotel_cost)
        return activity_tuple
