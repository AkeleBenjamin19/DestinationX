#!/usr/bin/env python
# scripts/test_destinations_pages.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root on path
top = Path(__file__).parents[2]
sys.path.insert(0, str(top))

from app import create_app
from app.services.reccommendation_service import RecommendationService
from app.models.city import City
from app.models.country import Country


def main():
    # Load env and create app
    load_dotenv(top / ".env")
    app = create_app()

    # Use Flask test client
    client = app.test_client()

    with app.app_context():
        # Instantiate recommendation service
        rec_service = RecommendationService()
        # Get available destinations
        countries = rec_service.get_available_destinations()
        if not countries:
            print("No available destinations to test.")
            return
        country = countries[0]
        # Choose first city
        city = City.query.filter_by(country_id=country.id).first()
        if not city:
            print(f"No city found for country {country.name} (ID={country.id})")
            return

    # Test /destinations
    resp = client.get('/destinations/')
    print('GET /destinations/ ->', resp.status_code)
    print(resp.data.decode('utf-8')[:500], '...')

    # Test /destination/<country_id>/<city_id>
    url = f'/destination/{country.id}/{city.id}'
    resp2 = client.get(url)
    print(f'GET {url} ->', resp2.status_code)
    print(resp2.data.decode('utf-8')[:500], '...')

if __name__ == '__main__':
    main()
