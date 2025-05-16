# Author: Akele Benjamin
# This script fetches all activities from a JSON file, parses them into standardized records, and saves them to the database.
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1) Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# 2) Load environment variables (DATABASE_URL, etc.)
load_dotenv(PROJECT_ROOT / ".env")

# 3) Imports
from app import create_app
from app.services.activity_service import ActivityService


def main():
    # Initialize Flask app and application context
    app = create_app()
    with app.app_context():
        service = ActivityService()

        # Step 1: Read raw JSON data
        data = service.read_json()
        print(f"Loaded {len(data)} activity records from {service.json_path}")

        # Step 2: Parse into standardized records
        records = service.parse_activities(data)
        print(f"Parsed {len(records)} activity entries for processing.")

        # Step 3: Save into the database
        service.save_activities(records)
        print(f"Saved {len(records)} activities to the database.")

if __name__ == '__main__':
    main()
#!/usr/bin/env python
# app/scripts/import_activities.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1) Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# 2) Load environment variables (DATABASE_URL, etc.)
load_dotenv(PROJECT_ROOT / ".env")

# 3) Imports
from app import create_app
from app.services.activity_service import ActivityService


def main():
    # Initialize Flask app and application context
    app = create_app()
    with app.app_context():
        service = ActivityService()

        # Step 1: Read raw JSON data
        data = service.read_json()
        print(f"Loaded {len(data)} activity records from {service.json_path}")

        # Step 2: Parse into standardized records
        records = service.parse_activities(data)
        print(f"Parsed {len(records)} activity entries for processing.")

        # Step 3: Save into the database
        service.save_activities(records)
        print(f"Saved {len(records)} activities to the database.")

if __name__ == '__main__':
    main()
