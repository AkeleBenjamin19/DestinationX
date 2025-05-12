"""Author: Akele Benjamin"""

import os
import math
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

class Hotel_API:
    """
    Simulates hotel searches using a local JSON dataset which has the same format as Google Places.
    Provides methods to load raw hotel entries, process and score them by amenities,
    extract fields for database storage, and persist individual hotels.
    
    """

    def __init__(self,
                 raw_data_file: str,
                 radius: int = 5000,
                 max_results: int = 20,
                 max_radius: int = 50000):
        """
        Args:
            raw_data_file: Path to the JSON file containing hotel entries
                           (each entry must include name, formatted_address,
                           geometry.location.lat/lng, amenities list, rating).
            radius:       Initial search radius (simulated; not used for filtering file data).
            max_results:  Maximum number of hotels to load from the JSON.
            max_radius:   Maximum radius for search expansion (not used in simulation).
        """
        load_dotenv()
        self.raw_data_file = raw_data_file
        self.initial_radius = radius
        self.max_results = max_results
        self.max_radius = max_radius

    def find_hotels(self, latitude: float, longitude: float) -> list[dict]:
        """
        Load raw hotel entries from the JSON file and return up to max_results entries.

        Args:
            latitude:  Origin latitude (for interface consistency; not used here).
            longitude: Origin longitude (for interface consistency; not used here).

        Returns:
            List of hotel dicts as read from the JSON file.
        """
        with open(self.raw_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # support either a top-level list or a dict with "results" key
        hotels = data.get('results', data) if isinstance(data, dict) else data
        return hotels[:self.max_results]

    def process_hotels(self,
                       raw_hotels: list[dict],
                       latitude: float,
                       longitude: float,
                       amenities: list[str]) -> list[dict]:
        """
        Score hotels by how many requested amenities they include,
        compute distance, then sort by match_score (fallback to rating).

        Args:
            raw_hotels:  List of dicts from find_hotels().
            latitude:    Origin latitude for distance calculation.
            longitude:   Origin longitude for distance calculation.
            amenities:   Desired amenities list.

        Returns:
            Sorted list of enriched hotel dicts with keys:
              - name, address, location, amenities, match_score, distance_m, rating
        """
        processed = []
        for place in raw_hotels:
            hotel_amenities = place.get('amenities', [])
            match_score = len(set(amenities).intersection(hotel_amenities))
            loc = place.get('geometry', {}).get('location', {})
            dist = self._distance(latitude, longitude,
                                  loc.get('lat', 0), loc.get('lng', 0))
            processed.append({
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'location': loc,
                'amenities': hotel_amenities,
                'match_score': match_score,
                'distance_m': dist,
                'rating': place.get('rating', 0)
            })

        # sort by amenity match
        processed.sort(key=lambda h: h['match_score'], reverse=True)
        # fallback if no matches
        if processed and processed[0]['match_score'] == 0:
            processed.sort(key=lambda h: h['rating'], reverse=True)

        return processed

    def extract_hotels(self,
                       raw_hotels: list[dict],
                       latitude: float,
                       longitude: float,
                       airport: str) -> list[dict]:
        """
        Extract only the fields needed for DB insertion from raw hotel entries.

        Args:
            raw_hotels:  List of dicts from find_hotels().
            latitude:    Origin latitude for distance calculation.
            longitude:   Origin longitude for distance calculation.
            airport:     Airport identifier (e.g., IATA code).

        Returns:
            List of hotel-record dicts with keys:
              airport, name, address, latitude, longitude,
              amenities (list), distance_m, rating
        """
        extracted = []
        for place in raw_hotels:
            loc = place.get('geometry', {}).get('location', {})
            dist = self._distance(latitude, longitude,
                                  loc.get('lat', 0), loc.get('lng', 0))
            extracted.append({
                'airport': airport,
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'latitude': loc.get('lat'),
                'longitude': loc.get('lng'),
                'amenities': place.get('amenities', []),
                'distance_m': dist,
                'rating': place.get('rating', 0)
            })
        return extracted

    def store_hotel(self, hotel: dict) -> None:
        """
        Persist a single hotel record to the Postgres `hotels` table.

        Expects `hotels` schema:
            airport TEXT,
            name TEXT,
            address TEXT,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            amenities JSONB,
            distance_m DOUBLE PRECISION,
            rating DOUBLE PRECISION
        """
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cur = conn.cursor()
        insert_sql = (
            "INSERT INTO hotels"
            " (airport, name, address, latitude, longitude, amenities, distance_m, rating)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT DO NOTHING"
        )
        cur.execute(insert_sql, (
            hotel['airport'],
            hotel['name'],
            hotel['address'],
            hotel['latitude'],
            hotel['longitude'],
            json.dumps(hotel['amenities']),
            hotel['distance_m'],
            hotel['rating']
            #Taking in airport string or airport id.
        ))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def _distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate Haversine distance (in meters) between two lat/lng points."""
        R = 6371000  # Earth radius in meters
        φ1, φ2 = map(math.radians, (lat1, lat2))
        Δφ = math.radians(lat2 - lat1)
        Δλ = math.radians(lng2 - lng1)
        a = math.sin(Δφ/2)**2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
