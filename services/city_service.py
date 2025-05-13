import os
import requests
from pathlib import Path
from typing import List, Dict, Tuple
from .. import db
from app.models.country import Country
from app.models.city import City

# Directory containing data files
DATA_DIR = Path(__file__).parents[1] / 'data'


def parse_city_country(filename: str = 'top_100_cities.txt') -> List[Dict[str, str]]:
    """
    Read a file of lines "City, Country" and return a list of dicts:
      [{'city': 'London', 'country': 'United Kingdom'}, ...]
    """
    path = DATA_DIR / filename
    pairs: List[Dict[str, str]] = []
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            parts = line.split(',', 1)
            if len(parts) != 2:
                continue
            city, country = parts[0].strip(), parts[1].strip()
            pairs.append({'city': city, 'country': country})
    return pairs


def geocode_city(city: str, country: str) -> Tuple[float, float]:
    """
    Look up latitude and longitude using OpenStreetMap Nominatim.
    """
    url = 'https://nominatim.openstreetmap.org/search'
    params = {'q': f'{city}, {country}', 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'destination-x-app/1.0 (admin@example.com)'}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    results = resp.json()

    if not results:
        raise ValueError(f"No geocoding result for {city}, {country}")

    lat = float(results[0]['lat'])
    lng = float(results[0]['lon'])
    return lat, lng


def save_cities(city_country_list: List[Dict[str, str]]) -> None:
    """
    Given a list of {'city','country'} dicts, geocode and upsert into the cities table.
    """
    # Build country name -> id map
    all_countries = Country.query.all()
    country_map = {c.name: c.id for c in all_countries}

    for entry in city_country_list:
        name = entry['city']
        country_name = entry['country']

        country_id = country_map.get(country_name)
        if country_id is None:
            print(f"[SKIP] Country not found: {country_name}")
            continue

        try:
            lat, lng = geocode_city(name, country_name)
        except Exception as e:
            print(f"[ERROR] Geocode failed for {name}, {country_name}: {e}")
            continue

        # Upsert city
        city = City.query.filter_by(name=name, country_id=country_id).first()
        if city:
            city.latitude = lat
            city.longitude = lng
        else:
            city = City(name=name, country_id=country_id, latitude=lat, longitude=lng)
            db.session.add(city)

    db.session.commit()
