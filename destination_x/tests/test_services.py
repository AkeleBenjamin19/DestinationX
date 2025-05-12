import unittest 
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

from app.services.recommendation import Recommendation
from app.utils.fake_data import generate_fake_data

from app.models.user import User
from app.models.activity import Activity
from app.models.country import Country
from app.models.city import City
from app.models.visa import Visa_policies

class TestRecommendation(unittest.TestCase):
    def setUp(self):

        with app.app_context():
            generate_fake_data()

            """Create a Recommendation object and get the list of activities and visa policies"""
            """Get the list of activities and visa policies from the database"""
            try:
                user_budget = 1000000
                lst_of_activities = Activity.query.all()
                #what is the equivalent of query.all() of activity
                activity_lst = [(activity.name, activity.weight, activity.cost, activity.f_cost, activity.h_cost) for activity in lst_of_activities]
                                
                policies = Visa_policies.query.all()
                visa_policies = {}
                for visa in policies:
                    visa_policies["visa_free"] = visa.visa_free
                    visa_policies["destination_id"] = visa.destination_id
                    visa_policies["e_visa"] = visa.e_visa
                    visa_policies["visa_required"] = visa.visa_required
                    
                self.recommendation = Recommendation(user_budget, activity_lst, visa_policies)
            except Exception as e:
                print("Error with generating fake data:", e)

        
    """Test the _recommender method"""
    def test_recommender(self):
        """Test the _recommender method"""
        result = self.recommendation._recommender()
        self.assertIsNotNone(result)
        pass
       

    def test_max_ranked_destinations(self):
        """Test the _max_ranked_destinations method"""
        self.recommend = Recommendation()
        result = self.recommend.max_ranked_destinations([("Italy", "Rome", 0.8),("France","Paris", 0.9), ("Spain", "Madrid", 0.7)])
        self.assertListEqual(result, [("France","Paris", 0.9), ("Italy", "Rome", 0.8)])

      
            

    # def test_insert_recommendations(self):
    #     result = self.recommendation._insert_recommendations([])
    #     self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()