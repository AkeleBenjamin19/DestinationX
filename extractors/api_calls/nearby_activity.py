"""Author: Akele Benjamin"""
import os
import json
import math
import psycopg2
from dotenv import load_dotenv

class Nearby_Activity:
    """
    Simulates Google Places 'nearbysearch' for activities using a local JSON file.
    Categorizes activities into walking and driving distance buckets,
    filters by categories, and can persist entries to Postgres.
    """

    def __init__(self,
                 raw_data_file: str,
                 walking_radius_m: int = 1000,
                 driving_radius_m: int = 5000):
        """
        Args:
            raw_data_file:    Path to the JSON file containing activity entries.
            walking_radius_m: Max distance (m) classified as walking distance.
            driving_radius_m: Max distance (m) classified as driving distance.
        """
        load_dotenv()
        self.raw_data_file = raw_data_file
        self.walking_radius = walking_radius_m
        self.driving_radius = driving_radius_m

    def find_activities(self,
                        latitude: float,
                        longitude: float) -> dict[str, list[dict]]:
        """
        Simulate a Google Places Nearby Search for activities.

        Returns a dict with:
          - 'walking':  activities within walking_radius
          - 'driving':  activities beyond walking_radius up to driving_radius
        """
        with open(self.raw_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        activities = data.get('results', data) if isinstance(data, dict) else data

        walking, driving = [], []
        for act in activities:
            loc = act.get('geometry', {}).get('location', {})
            dist = self._distance(latitude,
                                  longitude,
                                  loc.get('lat', 0),
                                  loc.get('lng', 0))
            record = {
                'name': act.get('name'),
                'category': act.get('category', 'unknown'),
                'location': loc,
                'distance_m': dist
            }
            if dist <= self.walking_radius:
                walking.append(record)
            elif dist <= self.driving_radius:
                driving.append(record)

        return {'walking': walking, 'driving': driving}

    def interested_activities(self,
                              categories: list[str]) -> list[dict]:
        """
        Filter all activities by matching any of the provided categories.
        """
        with open(self.raw_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        activities = data.get('results', data) if isinstance(data, dict) else data
        return [
            {
                'name': act.get('name'),
                'category': act.get('category'),
                'location': act.get('geometry', {}).get('location', {}),
                'distance_m': None
            }
            for act in activities
            if act.get('category') in categories
        ]

    def store_activity(self, activity: dict) -> None:
        """
        Persist a single activity record to the Postgres `activities` table.

        Expected table schema:
            name TEXT,
            category TEXT,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            distance_m DOUBLE PRECISION
        """
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cur = conn.cursor()
        insert_sql = (
            "INSERT INTO activities"
            " (name, category, latitude, longitude, distance_m)"
            " VALUES (%s, %s, %s, %s, %s)"
            " ON CONFLICT DO NOTHING"
        )
        loc = activity.get('location', {})
        cur.execute(insert_sql, (
            activity.get('name'),
            activity.get('category'),
            loc.get('lat'),
            loc.get('lng'),
            activity.get('distance_m')
        ))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def _distance(lat1: float,
                  lng1: float,
                  lat2: float,
                  lng2: float) -> float:
        """
        Calculate Haversine distance (in meters) between two lat/lng points.
        """
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)
        a = (math.sin(dphi/2)**2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2)
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

