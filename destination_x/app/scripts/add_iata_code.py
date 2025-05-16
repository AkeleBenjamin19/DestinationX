# Author: Akele Benjamin
# This script adds unique categories to the database from the Activity model.


import os
from pathlib import Path
import sys
from amadeus import Client, ResponseError
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parents[2]   
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")     
from run import create_app
from app import db
from app.models.city import City

def main():

    app = create_app()
    with app.app_context():

        amadeus = Client(
            client_id=os.environ['AMADEUS_CLIENT_ID'],
            client_secret=os.environ['AMADEUS_CLIENT_SECRET']
        )

        #Fetch all cities
        cities = City.query.all()
        for city in cities:
            try:
                #Lookup by city name, subType='CITY'
                resp = amadeus.reference_data.locations.get(
                    keyword=city.name,
                    subType='CITY'
                )
                data = resp.data or []
                if data:
                    code = data[0].get('iataCode')
                    if code:
                        city.iata_code = code
                        db.session.add(city)
                        print(f"{city.name:<30} → {code}")
                    else:
                        print(f"{city.name:<30} → no iataCode in response")
                else:
                    print(f"{city.name:<30} → no matches")
            except ResponseError as err:
                print(f"{city.name:<30} → ERROR: {err}")

        # Commit all updates in one go
        db.session.commit()
        print("Done updating IATA codes.")

if __name__ == '__main__':
    main()
