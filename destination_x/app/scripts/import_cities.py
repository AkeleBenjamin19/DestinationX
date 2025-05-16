# Author : Akele Benjamin
# This script imports city data from a txt file from https://en.wikipedia.org/wiki/List_of_cities_by_international_visitors and saves it to the database. 

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


load_dotenv(PROJECT_ROOT / ".env")

# 3) Import the Flask application factory and city service
from app import create_app
from app.services.city_service import (
    parse_city_country,
    geocode_city,
    save_cities
)


def main():
    # Create and configure the Flask app
    app = create_app()
    with app.app_context():
        # Parse city-country pairs from data file
        city_entries = parse_city_country()
        print(f"Parsed {len(city_entries)} city entries.")

        # Geocode & save to the cities table
        save_cities(city_entries)
        print("All cities have been saved to the database.")


if __name__ == "__main__":
    main()