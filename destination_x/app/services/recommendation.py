"""Author: Shamar Malcolm"""


"""Import packages"""
# from app.utils.connectDB import connect_db


# from app.models import User
#replace all uses of raw sql and connectdb with SQLAlchemy

from app import app,db
from app.models.activity import Activity 
from app.models.country import Country
from app.models.city import City
from app.models.flight_price import FlightPrice
from app.models.hotel import Hotel
class Recommendation:
    """
    This class is responsible for making recommendations to the user
    It includes the user budget, list of activities, and visa policies.
    It runs computations on the data and returns a list of recommended destinations
    """

    """"
    Data representation of activity
    lst_of_activities = [(activity_name, weight_value, activity_cost, flight_cost, hotel_cost)]

    """
    def __init__(self, user_budget: float, lst_of_activities: list, visa_policies: dict) -> None:
        self.user_budget = user_budget
        self.lst_of_activities = lst_of_activities
        self.visa_policies = visa_policies


    def max_10_ranked_destinations(self, lst_of_destinations : list) -> list:
        try:
            lst_of_destinations.sort(key=lambda x: x[2], reverse=True)
            lst_of_destinations = list(filter(lambda x: x[2] >= 0.80, lst_of_destinations))
            return lst_of_destinations[:10]
        except Exception as e:
            print("Error with sorting destinations:", e)

    def _recommender(self) -> list:
        """Returns a list of the highest ranked destinations for the user"""
        with app.app_context():

            # query_country = "SELECT name FROM countries"

            
            countries = db.session.execute(db.select(Country.name).order_by(Country.name)).scalars().all()

            destination_information = []
            
            for country in countries:
                country_information = []
                country_activity_costs = 0
                country_flight_costs = 0
                country_hotel_costs = 0
                for activity in self.lst_of_activities:
                    
                    #for the query below write in sqlalchemy
                    # query = "SELECT countries.name FROM countries JOIN cities ON countries.id = cities.country_id JOIN activities ON activities.city_id = cities.id WHERE activities.name = %s"
                    query = db.session.query(Country.name).join(City, City.country_id == Country.id).join(Activity, Activity.city_id == City.id).filter(Activity.name == activity[0]).all()
                    activity_country = [country.name for country in query]
                    # activity_country = cursor.execute(query, (activity[0])).fetchall()
                    # activity_country = query
                    if country not in activity_country:
                        is_activity_in_location = 0
                    else:
                        is_activity_in_location = 1
                        country_activity_costs += activity[2]
                        country_flight_costs += activity[3]
                        country_hotel_costs += activity[4]
                    country_information.append((country, activity[1], is_activity_in_location))
                    
                weight_sum = sum(info[1] for  info in country_information if info[2] == 1)
                total_weight = sum(info[1] for info in country_information)
                
                def calculate_score(sum_of_weights, budget, flight_cost, hotel_cost, activity_cost):
                    budget_ratio = budget/(flight_cost + hotel_cost + activity_cost)
                    percentage_score = (sum_of_weights/total_weight) * budget_ratio * 100
                    return percentage_score
                
                """Score calculation formula"""
              
                similarity_percentage = calculate_score(weight_sum, self.user_budget, country_flight_costs, country_hotel_costs, country_activity_costs)

                # city_query = "SELECT name FROM cities JOIN countries ON countries.id = cities.country_id WHERE countries.name = %s"
                city_query = db.session.query(City.name).join(Country, Country.id == City.country_id).filter(Country.name == country).first()
                # city = cursor.execute(city_query, (country))
                city = city_query.name
                #remove city 

                destination_information.append((country, city, similarity_percentage))
                # print(destination_information)
            # """Filters destination information based on visa policies"""
            # if self.visa_policies["visa_free"] == True:
            #     # visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.destination_id WHERE visa_policies.visa_free = %s"
            #     visa_search =  db.session.query(Country).join(Visa_policies, Country.id == Visa_policies.destination_id).filter(Visa_policies.visa_free == True).all()
            #     # visa_free_countries = cursor.execute(visa_search, (True)).fetchall()

            #     visa_free_countries = [country.name for country in visa_search]


            #     """List of destinations with free visas"""
            #     destination_information = filter(lambda x: x[0] in visa_free_countries, destination_information)
                
            # elif self.visa_policies["visa_required"] == True:
            #     # visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.destination_id WHERE visa_policies.visa_required = %s"
            #     visa_search = db.session.query(Country).join(Visa_policies, Country.id == Visa_policies.destination_id).filter(Visa_policies.visa_required == True).all()
            #     # visa_required_countries = cursor.execute(visa_search, (True)).fetchall()
            #     visa_required_countries = [country.name for country in visa_search]

            #     """List of destinations with required visas"""
            #     destination_information = filter(lambda x: x[0] in visa_required_countries, destination_information)
            # # elif self.visa_policies["without_passport"] == True:
            # #     visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.destination_id WHERE visa_policies.without_passport = %s"
            # #     without_passport_countries = cursor.execute(visa_search, (True)).fetchall()

            # #     """List of destinations with required visas"""
            # #     destination_information = filter(lambda x: x[0] in without_passport_countries, destination_information)
                
        
            # elif self.visa_policies["e_visa"] == True:
            #     # visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.destination_id WHERE visa_policies.e_visa = %s"
            #     visa_search = db.session.query(Country).join(Visa_policies, Country.id == Visa_policies.destination_id).filter(Visa_policies.e_visa == True).all()
            #     e_visa_countries = [country.name for country in visa_search]
            #     # e_visa_countries = cursor.execute(visa_search, (True)).fetchall()

            #     """List of destinations with e-visas"""
            #     destination_information = filter(lambda x: x[0] in e_visa_countries, destination_information)
            
            # """Inserts recommendations into the database"""
            # self.insert_recommendations(destination_information)

            # cursor.close()

            """Returns the top ten ranked destinations"""
            return self.max_10_ranked_destinations(destination_information)
    

    

    """Insert recommendations into the database for the current logged in user"""
    def _insert_recommendations(self, destinations : list)->None:
        
        pass


    