import faker

# from .connectDB import connect_db
from app import app,db 
from app.models.activity import Activity 
from app.models.country import Country
from app.models.city import City
from app.models.flight_price import FlightPrice
from app.models.hotel import Hotel
import random


class GenerateFakeData:
    def __init__(self):
        pass
    def generate_fake_data(self):
        fake = faker.Faker()
        continents = {
        "Africa": "AF",
        "Antarctica": "AN",
        "Asia": "AS",
        "Europe": "EU",
        "North America": "NA",
        "Oceania": "OC",
        "South America": "SA",
        }
        with app.app_context():
            for i in range(10):
                continent, code = random.choice(list(continents.items()))
                while True:
                    iso_code = fake.country_code()
                    if not Country.query.filter_by(iso_code=iso_code).first():
                        break

                while True:
                    name = fake.country()
                    if not Country.query.filter_by(name=name).first():
                        break
                country = Country(name, iso_code, continent, code)
                db.session.add(country)
                db.session.commit()

                city =  City(fake.name(), country.id, fake.latitude(), fake.longitude(), fake.image_url())
                db.session.add(city)
                db.session.commit()

                activity = Activity(fake.name(),city.id, fake.latitude(), fake.longitude(), random.randint(2000, 5000))
                db.session.add(activity)
                db.session.commit()

                city_ids = db.session.execute(db.select(City.id).order_by(City.id)).scalars().all()
            
                origin_city_id = random.choice(city_ids)

                flight_price = FlightPrice(origin_city_id,city.id , fake.date(), fake.date(), random.randint(20, 50), random.choice([200.23, 500.24, 1000.242, 34204.13]),\
                                fake.currency_code(), random.choice([342.2, 102.232, 493.234, 493.21, 453, 932.12]), random.randint(100, 200), fake.date_time())
                db.session.add(flight_price)
                db.session.commit()

                while True:
                    external_hotel_id = str(random.randint(10000, 20000))

                    if not Hotel.query.filter_by(external_hotel_id=external_hotel_id).first():
                        break
                
                hotel = Hotel(external_hotel_id, fake.name(), fake.address(), city.id, fake.latitude(), fake.longitude(), random.randint(200, 1000), random.randint(1, 5), random.randint(10000, 20000))
                #add user to database using not alchemy but commit
                db.session.add(hotel)
                db.session.commit()
        return