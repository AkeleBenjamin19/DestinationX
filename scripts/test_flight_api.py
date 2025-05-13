import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1) Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).parents[2]  # one level up from scripts/
sys.path.insert(0, str(PROJECT_ROOT))

# 2) Load environment variables (Amadeus creds, DATABASE_URL, etc.)
load_dotenv(PROJECT_ROOT / ".env")

from app import create_app
from app.services.flight_api_service import FlightAPIService


def main():
    # Create Flask app context
    app = create_app()
    with app.app_context():
        svc = FlightAPIService()
        
        # Sample data: New York (JFK) -> London (LHR)
        origin = 'MIA'
        destination = 'LHR'
        departure = '2025-07-01'
        return_date = '2025-07-10'
        adults = 1

        print(f"Fetching best flight from {origin} to {destination} on {departure} returned {return_date} for {adults} adult(s)")
        entries = svc.get_price_entries(origin, destination, departure, return_date, adults)

        if not entries:
            print("No flight entries found.")
            return

        for entry in entries:
            print("-- Flight Offer --")
            print(f"Origin City ID:      {entry['origin_city_id']}")
            print(f"Destination City ID: {entry['destination_city_id']}")
            print(f"Departure Date:      {entry['departure_date']}")
            print(f"Return Date:         {entry['return_date']}")
            print(f"Adults:              {entry['adults']}")
            print(f"Currency:            {entry['currency_code']}")
            print(f"Best Price:          {entry['best_price']}")
            print(f"Stops Allowed:       {entry['stops_allowed']}")
            print(f"Fetched At:          {entry['fetched_at']}\n")

        # Optional: save entries to DB
        # svc.save_temp_prices(entries)
        # print("Entries saved to database.")

if __name__ == '__main__':
    main()
