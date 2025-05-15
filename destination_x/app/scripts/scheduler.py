""" Scheduler for import jobs
This script sets up a scheduler to run various import jobs at specified intervals.
The jobs include:
- Importing country data from an external API
- Importing city data from a Wikipedia page
- Importing visa policies from an external API
- Importing airport data from a CSV file"""


__author__ = "Akele Benjamin(620130803)"
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent[2]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

#Import job entrypoints
from app.scripts.import_countries import main as import_countries_main
from app.scripts.import_cities import main as import_cities_main
from app.scripts.import_all_visas import main as import_all_visas_main
from app.scripts.import_airports import main as import_airports_main

# 4) Scheduler setup
from apscheduler.schedulers.blocking import BlockingScheduler

def schedule_jobs():
    scheduler = BlockingScheduler()

    # Yearly jobs: countries and cities
    scheduler.add_job(
        import_countries_main,
        'cron',
        month=1, day=1, hour=0, minute=0,
        id='import_countries'
    )
    scheduler.add_job(
        import_cities_main,
        'cron',
        month=1, day=1, hour=1, minute=0,
        id='import_cities'
    )

    # Monthly job: visa policies on the 1st of each month
    scheduler.add_job(
        import_all_visas_main,
        'cron',
        day=1, hour=2, minute=0,
        id='import_visas'
    )

    # Weekly job: airport import every Monday
    scheduler.add_job(
        import_airports_main,
        'cron',
        day_of_week='mon', hour=3, minute=0,
        id='import_airports'
    )

    print("Scheduled jobs:")
    print(" - import_countries: yearly at Jan 1 00:00")
    print(" - import_cities:   yearly at Jan 1 01:00")
    print(" - import_visas:    monthly on day 1 at 02:00")
    print(" - import_airports: weekly on Mondays at 03:00")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")


if __name__ == '__main__':
    schedule_jobs()
