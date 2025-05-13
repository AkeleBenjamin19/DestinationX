import json
from pathlib import Path
from typing import List, Dict, Any

from .. import db
from app.models.activity import Activity
from app.models.city import City

class ActivityService:
    """
    Service for loading activity data from a JSON file, parsing it, and saving to the database.
    """
    def __init__(self, json_path: Path = None):
        # Default path: app/data/activities.json
        data_dir = Path(__file__).parents[1] / 'data'
        self.json_path = json_path or (data_dir / 'activities.json')

    def read_json(self) -> List[Dict[str, Any]]:
        """
        Load the raw JSON list of activity entries from file.
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def parse_activities(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract the fields needed for Activity model.
        """
        records: List[Dict[str, Any]] = []
        for entry in data:
            city_name = entry.get('city')
            geom = entry.get('geometry', {}).get('location', {})
            records.append({
                'name': entry.get('name'),
                'category': entry.get('category'),
                'latitude': geom.get('lat'),
                'longitude': geom.get('lng'),
                'price': entry.get('cost'),
                'city_name': city_name
            })
        return records

    def save_activities(self, records: List[Dict[str, Any]]) -> None:
        """
        Upsert activity records into the activities table, matching by name+city.
        """
        # Build city name -> id map
        cities = City.query.all()
        city_map = {c.name: c.id for c in cities}

        for r in records:
            city_id = city_map.get(r['city_name'])
            if not city_id:
                print(f"[SKIP] City not found: {r['city_name']}")
                continue

            # Check if activity exists
            act = Activity.query.filter_by(name=r['name'], city_id=city_id).first()
            if act:
                # update
                act.category  = r['category']
                act.latitude  = r['latitude']
                act.longitude = r['longitude']
                act.price     = r['price']
            else:
                # insert
                act = Activity(
                    name       = r['name'],
                    category   = r['category'],
                    city_id    = city_id,
                    latitude   = r['latitude'],
                    longitude  = r['longitude'],
                    price      = r['price']
                )
                db.session.add(act)

        db.session.commit()