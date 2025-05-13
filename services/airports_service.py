import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

from .. import db
from app.models.airport import Airport
from app.models.city import City

class AirportService:
    """
    Service for loading airport data from an Excel file and saving it to the DB.
    """
    def __init__(self, excel_path: Path = None):
        # Default path to data directory: app/data/airports.xlsx
        data_dir = Path(__file__).parents[1] / 'data'
        self.excel_path = excel_path or (data_dir / 'airports.xlsx')

    def read_excel(self) -> pd.DataFrame:
        """
        Read the airports Excel file into a DataFrame.
        """
        df = pd.read_excel(self.excel_path)
        return df

    def parse_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract relevant fields from the DataFrame into a list of dictionaries.
        """
        records: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            records.append({
                'ident':         row.get('ident'),
                'type':          row.get('type'),
                'name':          row.get('name'),
                'iata_code':     row.get('iata_code'),
                'iso_country':   row.get('iso_country'),
                'iso_region':    row.get('iso_region'),
                'latitude_deg':  row.get('latitude_deg'),
                'longitude_deg': row.get('longitude_deg'),
                'municipality':  row.get('municipality')
            })
        return records

    def save_to_db(self, records: List[Dict[str, Any]]) -> None:
        """
        Upsert airport records into the database.
        Associates airports with existing cities by municipality name.
        """
        # Build mapping: city name -> city ID
        cities = City.query.all()
        city_map = {c.name: c.id for c in cities}

        for rec in records:
            ident = rec['ident']
            city_name = rec['municipality']
            city_id = city_map.get(city_name)
            if city_id is None:
                print(f"[SKIP] City not found: {city_name}")
                continue

            airport = Airport.query.filter_by(ident=ident).first()
            if airport:
                # Update existing record
                airport.type        = rec['type']
                airport.name        = rec['name']
                airport.iata_code   = rec['iata_code']
                airport.iso_country = rec['iso_country']
                airport.iso_region  = rec['iso_region']
                airport.latitude    = rec['latitude_deg']
                airport.longitude   = rec['longitude_deg']
                airport.city_id     = city_id
            else:
                # Insert new record
                airport = Airport(
                    ident         = rec['ident'],
                    type          = rec['type'],
                    name          = rec['name'],
                    iata_code     = rec['iata_code'],
                    iso_country   = rec['iso_country'],
                    iso_region    = rec['iso_region'],
                    latitude      = rec['latitude_deg'],
                    longitude     = rec['longitude_deg'],
                    city_id       = city_id
                )
                db.session.add(airport)

        db.session.commit()
