"""HotelAPIService
Service for loading hotel data from a JSON file,
finding the best match by amenities and dynamic pricing,
and saving hotels to the database.
"""

__author__ = "Akele Benjamin(620130803)"
import json
from pathlib import Path
from typing import List, Dict, Any, Union
from datetime import datetime, date

from .. import db
from app.models.hotel import Hotel
from app.models.city import City

class HotelAPIService:
    """
    Service for loading hotel data from a JSON file,
    finding the best match by amenities and dynamic pricing,
    and saving hotels to the database.
    """
    def __init__(self, json_path: Path = None):
        # Default to app/data/hotels.json
        data_dir = Path(__file__).parents[1] / 'data'
        self.json_path = json_path or (data_dir / 'hotels.json')

    def read_json(self) -> List[Dict[str, Any]]:
        """
        Load the raw JSON list of hotel entries from file.
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def parse_hotels(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract only the fields needed for processing and DB storage.
        """
        records: List[Dict[str, Any]] = []
        for entry in data:
            records.append({
                'name': entry['name'],
                'address': entry['formatted_address'],
                'latitude': entry['geometry']['location']['lat'],
                'longitude': entry['geometry']['location']['lng'],
                'amenities': entry.get('amenities', []),
                'rating': entry.get('rating', 3.0),
                'city_name': entry.get('city')
            })
        return records

    def generate_price(self,
                       rating: float,
                       num_persons: int,
                       amenities: List[str],
                       check_in: Union[str, date, datetime],
                       check_out: Union[str, date, datetime]) -> float:
        """
        Calculate booking cost:
          days between check_in and check_out *
          (rating * num_persons * number of amenities * 2)
        Dates can be ISO strings or date/datetime objects.
        """
        # normalize dates
        def to_date(d):
            if isinstance(d, str):
                return datetime.fromisoformat(d).date()
            if isinstance(d, datetime):
                return d.date()
            return d

        ci = to_date(check_in)
        co = to_date(check_out)
        days = (co - ci).days
        if days <= 0:
            return 0.0
        base = rating * num_persons * len(amenities) * 2
        return days * base

    def find_best_hotel(self,
                        city_name: str,
                        required_amenities: List[str],
                        num_persons: int,
                        check_in: Union[str, date, datetime],
                        check_out: Union[str, date, datetime]) -> Dict[str, Any]:
        """
        Among hotels in a given city, pick the one that:
          1) Matches the most of required_amenities.
          2) If tied, has the lowest generated price.
          3) If no amenities match, returns the hotel with the cheapest generated price.

        Returns a dict including a 'calculated_price' key.
        """
        all_data = self.parse_hotels(self.read_json())
        # filter hotels by city
        city_hotels = [h for h in all_data if h['city_name'] == city_name]
        if not city_hotels:
            return {}

        best_hotel: Dict[str, Any] = {}
        best_score = -1
        best_price = float('inf')

        for h in city_hotels:
            # calculate score & price
            score = sum(1 for a in required_amenities if a in h['amenities'])
            price = self.generate_price(h['rating'], num_persons, h['amenities'], check_in, check_out)

            # choose by score, then price
            if score > best_score or (score == best_score and price < best_price):
                best_hotel = h.copy()
                best_score = score
                best_price = price

        # if no amenities matched, ensure we pick cheapest
        if best_score == 0:
            cheapest = min(
                city_hotels,
                key=lambda x: self.generate_price(x['rating'], num_persons, x['amenities'], check_in, check_out)
            )
            best_hotel = cheapest.copy()
            best_price = self.generate_price(
                cheapest['rating'], num_persons, cheapest['amenities'], check_in, check_out
            )

        # attach calculated price
        best_hotel['calculated_price'] = best_price
        return best_hotel

    def save_hotels(self, records: List[Dict[str, Any]]) -> None:
        """
        Upsert a list of hotel dicts into the `hotels` table. Matches on name+city.
        """
        cities = City.query.all()
        city_map = {c.name: c.id for c in cities}

        for r in records:
            city_id = city_map.get(r['city_name'])
            if not city_id:
                print(f"[SKIP] City not in DB: {r['city_name']}")
                continue

            hotel = Hotel.query.filter_by(name=r['name'], city_id=city_id).first()
            if hotel:
                hotel.address   = r['address']
                hotel.latitude  = r['latitude']
                hotel.longitude = r['longitude']
                hotel.rating    = r.get('rating', hotel.rating)
                # price field can be left or updated as base cost
                hotel.price     = r.get('price', hotel.price)
            else:
                hotel = Hotel(
                    name=r['name'],
                    address=r['address'],
                    latitude=r['latitude'],
                    longitude=r['longitude'],
                    rating=r.get('rating'),
                    price=0.0,
                    city_id=city_id
                )
                db.session.add(hotel)

        db.session.commit()
