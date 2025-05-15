"""This script:
imports activity data from a JSON file into the database.
It reads the JSON file, parses the data into a standardized format,
and saves it to the database using the ActivityService class.
The script is designed to be run as a standalone script.
"""
#Command to run this script:
# python  app\scripts\import_activities.py

__author__ = "Akele Benjamin(620130803)"
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


load_dotenv(PROJECT_ROOT / ".env")


from app import create_app
from app.services.activity_service import ActivityService


def main():
    app = create_app()
    with app.app_context():
        service = ActivityService()

        data = service.read_json()
        print(f"Loaded {len(data)} activity records from {service.json_path}")

        records = service.parse_activities(data)
        print(f"Parsed {len(records)} activity entries for processing.")

        service.save_activities(records)
        print(f"Saved {len(records)} activities to the database.")

if __name__ == '__main__':
    main()
