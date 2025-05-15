""" This script:
Parses hotel data from a JSON file and saves it to the database.
This script reads the hotel data from the JSON file, parses it into a list of dictionaries,
and saves the records to the database using the HotelAPIService class.
The script is designed to be run as a standalone script.
"""


__author__ = "Akele Benjamin(620130803)"
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


top = Path(__file__).parents[2]
sys.path.insert(0, str(top))


load_dotenv(top / ".env")

from app import create_app
from app.services.hotel_api_service import HotelAPIService


def main():
    # Initialize Flask app and application context
    app = create_app()
    with app.app_context():
        service = HotelAPIService()

        # Read raw JSON data
        raw = service.read_json()
        print(f"Loaded {len(raw)} hotel records from {service.json_path}")

        # Parse into standardized records
        parsed = service.parse_hotels(raw)
        print(f"Parsed {len(parsed)} hotel entries for processing.")

        #  Save into the database
        service.save_hotels(parsed)
        print(f"Saved {len(parsed)} hotels to the database.")

if __name__ == '__main__':
    main()