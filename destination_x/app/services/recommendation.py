"""Authors: Shamar Malcolm"""


"""Import packages"""
from app.utils.connectDB import connect_db
from app.models import User

class Recommendation:
    
    """
    This class is responsible for making recommendations to the user
    It includes the user budget, list of activities, and visa policies.
    It runs computations on the data and returns a list of recommended destinations
    """
    def __init__(self, user_budget : int, lst_of_activities : list, visa_policies : dict) -> None:
        self.user_budget = user_budget
        self.lst_of_activities = lst_of_activities
        self.visa_policies = visa_policies


    def _recommender(self) -> list:

        """Returns a list of the highest ranked destinations for the user"""

        query_country = "SELECT name FROM countries"
        cursor = connect_db()
        countries = cursor.execute(query_country).fetchall()
        destination_information = []
        
        for country in countries:
            country_information = []
            for activity in self.lst_of_activities:
                query = "SELECT countries.name FROM countries JOIN cities ON countries.id = cities.country_id JOIN activities ON activities.city_id = cities.id WHERE activities.name = %s"
                activity_country = cursor.execute(query, (activity[0])).fetchall()
                if country not in activity_country:
                    is_activity_in_location = 0
                else:
                    is_activity_in_location = 1
                country_information.append(country, activity[1], is_activity_in_location)

            
            weight_sum = sum(info[1] for  info in country_information if info[2] == 1)
            activity_cost = sum(activity[2] for activity in self.lst_of_activities)
            flight_cost = sum(activity[3] for activity in self.lst_of_activities)
            hotel_cost = sum(activity[4] for activity in self.lst_of_activities)

            def calculate_score(sum_of_weights, budget, flight_cost, hotel_cost, activity_cost):
                return sum_of_weights + budget - flight_cost - hotel_cost - activity_cost
            
            """Score calculation formula"""
            user_expected_score = calculate_score(weight_sum, self.user_budget,flight_cost, hotel_cost, activity_cost)
            user_possible_outcomes = weight_sum + self.user_budget
            similarity_percentage = (user_expected_score / user_possible_outcomes) * 100

            city_query = "SELECT name FROM cities JOIN countries ON countries.id = cities.country_id WHERE countries.name = %s"
            city = cursor.execute(city_query, (country))
            destination_information.append((country, city, similarity_percentage))

        """Filters destination information based on visa policies"""
        if self.visa_policies["visa_free"] == True:
            visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.country_id WHERE visa_policies.visa_free = %s"
            visa_free_countries = cursor.execute(visa_search, (True)).fetchall()

            """List of destinations with free visas"""
            destination_information = filter(lambda x: x[0] in visa_free_countries, destination_information)
            
        elif self.visa_policies["visa_required"] == True:
            visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.country_id WHERE visa_policies.visa_required = %s"
            visa_required_countries = cursor.execute(visa_search, (True)).fetchall()

            """List of destinations with required visas"""
            destination_information = filter(lambda x: x[0] in visa_required_countries, destination_information)
        elif self.visa_policies["without_passport"] == True:
            visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.country_id WHERE visa_policies.without_passport = %s"
            without_passport_countries = cursor.execute(visa_search, (True)).fetchall()

            """List of destinations with required visas"""
            destination_information = filter(lambda x: x[0] in without_passport_countries, destination_information)
            
    
        elif self.visa_policies["e_visa"] == True:
            visa_search = "SELECT country from countries JOIN visa_policies ON countries.id = visa_policies.country_id WHERE visa_policies.e_visa = %s"
            e_visa_countries = cursor.execute(visa_search, (True)).fetchall()

            """List of destinations with e-visas"""
            destination_information = filter(lambda x: x[0] in e_visa_countries, destination_information)
        
        """Inserts recommendations into the database"""
        self.insert_recommendations(destination_information)

        cursor.close()

        """Returns the top ten ranked destinations"""
        return self.max_ranked_destinations(destination_information)
    

    """Returns the top ten ranked destinations that have a percentage score equal to or greater than 80"""
    def _max_ranked_destinations(self, lst_of_destinations : list) -> list:
        lst_of_destinations.sort(key=lst_of_destinations[2], reverse=True)
        lst_of_destinations = filter(lambda x: x[2] >= 0.80, lst_of_destinations)
        return lst_of_destinations
    

    """Insert recommendations into the database for the current logged in user"""
    def _insert_recommendations(self, destinations : list)->None:
        recommendation_insert= "INSERT INTO recommendations (user_id, city_id, score) VALUES (%s, %s, %s)"
        cursor = connect_db()
        user_query = User.query.filter_by(id= current_user.id).first()
        user_id = user_query.id
        for destination in destinations:
            cursor.execute(recommendation_insert, (user_id, destination[1], destination[2]))
            cursor.commit()
        cursor.close()
        

    
    
        



        









            






        


        


        

        


    
    
