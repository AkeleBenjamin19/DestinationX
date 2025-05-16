# Author: Akele Benjamin
# This script adds hotels to the database from a JSON file.

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

        # Step 1: Read raw JSON data
        raw = service.read_json()
        print(f"Loaded {len(raw)} hotel records from {service.json_path}")

        # Step 2: Parse into standardized records
        parsed = service.parse_hotels(raw)
        print(f"Parsed {len(parsed)} hotel entries for processing.")

        # Step 3: Save into the database
        service.save_hotels(parsed)
        print(f"Saved {len(parsed)} hotels to the database.")

if __name__ == '__main__':
    main()