import faker

# from .connectDB import connect_db
from app import app,db 
from app.models.user import User
from app.models.activity import Activity
from app.models.country import Country
from app.models.city import City
from app.models.visa import Visa_policies
import random


fake = faker.Faker()

def generate_fake_data():
    with app.app_context():
        for i in range(10):
            user = User(fake.name(), fake.email())
            #add user to database using not alchemy but commit
            db.session.add(user)
            db.session.commit()

            # cursor = connect_db()
            # cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (user._getUsername(), user._getEmail()))
            # cursor.commit()

            country = Country(fake.country())
            # cursor.execute("INSERT INTO countries (name) VALUES (%s)", (country._getName()))
            # cursor.commit()
            db.session.add(country)
            db.session.commit()

            
            

            
            city = City(fake.city(), country.id)
            # cursor.execute("INSERT INTO cities (name, country_id) VALUES (%s, %s)", (city._getName(), city._getCountryId()))
            # cursor.commit()
            db.session.add(city)
            db.session.commit()

            cities = City.query.all()
            city_id = [city.id for city in cities]
            activity_city = random.choice(city_id)
        

            activity = Activity(fake.sentence(), fake.random_int(min=1, max=10), fake.random_int(), fake.random_int(), fake.random_int(), activity_city)
            # cursor.execute("INSERT INTO activities (name, weight, cost, f_cost, h_cost) VALUES (%s, %s, %s, %s, %s)", (activity._getName(), activity._getWeight(), activity._getCost(), activity._getFlightCost(), activity._getHotelCost()))
            # cursor.commit()
            db.session.add(activity)
            db.session.commit()

            visa = Visa_policies(fake.boolean(), country.id, fake.boolean(), fake.boolean())
            # cursor.execute("INSERT INTO visa_policies (visa_free, destination_id, e_visa, visa_required) VALUES (%s, %s, %s, %s)", (visa._getVisaFree(), visa._getDestinationId(), visa._getEVisa(), visa._getVisaRequired()))
            # cursor.commit()

            # cursor.close()
            db.session.add(visa)
            db.session.commit()
    return