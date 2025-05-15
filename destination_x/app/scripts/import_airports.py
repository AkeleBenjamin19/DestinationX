""" This script:
 imports airport data from a subset of the excel file that is updated daily on https://davidmegginson.github.io/ourairports-data/airports.csv. The entire file was not used because this is a test project.
This script reads the excel file, parses it into a list of dictionaries, and saves the records to the database using the AirportService class."""

#Command to run this script:
# python  app\scripts\import_aiports.py
__author__ = "Akele Benjamin(620130803)"

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


load_dotenv(PROJECT_ROOT / ".env")

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
