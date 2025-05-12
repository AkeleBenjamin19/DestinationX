import os
import csv
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

class Airports_Pipeline:
    """
    A pipeline to extract airport data (from the web or a local CSV)
    and load selected fields into a Postgres `airports` table.
    """

    def __init__(self):
        # Load database credentials from .env (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
        load_dotenv()
        self.db_host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        # URL to the nightly-updated OurAirports CSV
        self.airports_csv_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"

    def extract_airports_website(self) -> list[dict]:
        """
        Fetches the latest airports CSV from the web and parses it into
        a list of dicts (one per airport).
        """
        resp = requests.get(self.airports_csv_url)
        resp.raise_for_status()
        reader = csv.DictReader(resp.text.splitlines())
        return list(reader)

    def extract_airports_csv(self, csv_filepath: str) -> list[dict]:
        """
        Reads a local airports CSV file(which is a subset of the complete csv file) that and parses it into a list of dicts.
        
        Args:
            csv_filepath: Path to the CSV file on disk.
        """
        with open(csv_filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def store_airports(self, airports: list[dict]) -> None:
        """
        Inserts selected fields for each airport into the `airports` table in Postgres.
        
        Expects a table schema:
            name         TEXT,
            latitude     DOUBLE PRECISION,
            longitude    DOUBLE PRECISION,
            continent    TEXT,
            iso_country  TEXT,
            municipality TEXT
        """
        conn = psycopg2.connect(
            host=self.db_host,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        cur = conn.cursor()

        # Prepare data tuples for bulk insertion
        records = [
            (
                a["name"],
                float(a.get("latitude_deg") or 0),
                float(a.get("longitude_deg") or 0),
                a.get("continent"),
                a.get("iso_country"),
                a.get("municipality"),
            )
            for a in airports
        ]

        insert_sql = """
            INSERT INTO airports
              (name, latitude, longitude, continent, iso_country, municipality)
            VALUES %s
            ON CONFLICT DO NOTHING
        """
        execute_values(cur, insert_sql, records)

        conn.commit()
        cur.close()
        conn.close()