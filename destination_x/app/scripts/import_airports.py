# Author: Akele Benjamin
# This script imports airport data from a subset of the excel file that is updated daily on https://davidmegginson.github.io/ourairports-data/airports.csv. The entire file was not used because this is a test project.
# python app/scripts/import_airports.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1) Make project root importable
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


load_dotenv(PROJECT_ROOT / ".env")

# 3) Import application factory and service
from app import create_app
from app.services.airports_service import AirportService


def main():
    # Initialize Flask app and DB context
    app = create_app()
    with app.app_context():
        service = AirportService()
        # Read Excel into DataFrame
        df = service.read_excel()
        print(f"Read {len(df)} rows from {service.excel_path}")

        # Parse into dict records
        records = service.parse_records(df)
        print(f"Parsed {len(records)} airport records.")

        # Save to database
        service.save_to_db(records)
        print(f"Saved {len(records)} airports to the database.")


if __name__ == '__main__':
    main()
