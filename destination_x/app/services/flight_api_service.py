"""
This Python script is a component of the Destination X service.

The script is designed to be run as a Flask web application, 
allowing for easy integration with other components of the 
Destination X service.

It fetches the chepeast flight price from the users location to their possible destinations with the following parameters:

    - Origin city/location
    - Destinaion city/location
    - Departure date
    - Return date
    - Number of passengers
    - Maximum price
    - Desired currency

It uses the Amadeus API to get flight prices and availability 
based on these criteria and displays them.

The chepeast flight offer is  with added filtering
for the following parameters:

    - City to IATA code conversion
    - Sorting my lowest price
    - Filtering by number of stops, with preference to direct flights
      where available. If not, 1 stop is allowed or the option with the least stops with the chepeast price.


Author:
        Xenique Daize , Member
        Destination X Team
        University of the West Indies, Mona.
        April 2025
Edited by:
        Akele Benjamin
"""

import asyncio
from functools import partial
import os
from datetime import datetime
from amadeus import Client, ResponseError
from .. import db
from app.models.flight_price import FlightPrice
from app.models.airport import Airport

class FlightAPIService:
    """
    Service to fetch flight offers from Amadeus and store temporary FlightPrice entries.
    """
    def __init__(self):
        # Initialize Amadeus API client using environment variables
        self.client = Client(
            client_id=os.environ.get('AMADEUS_CLIENT_ID'),
            client_secret=os.environ.get('AMADEUS_CLIENT_SECRET')
        )

    async def search_flight_offers(self,
                             origin_iata: str,
                             destination_iata: str,
                             departure_date: str,
                             return_date: str = None,
                             adults: int = 1,
                             max_results: int = 10) -> list:
        """
        Query Amadeus for flight offers between origin and destination.

        Returns a list of raw offer data dicts.
        """
        params = {
            'originLocationCode': origin_iata,
            'destinationLocationCode': destination_iata,
            'departureDate': departure_date,
            'adults': adults,
            'max': max_results
        }
        if return_date:
            params['returnDate'] = return_date

        try:
            response = await asyncio.to_thread(
        partial(self.client.shopping.flight_offers_search.get, **params)
    )
            return response.data
        except ResponseError as error:
            print(f"[Amadeus Error] {error}")
            return []

    async def get_price_entries(self,
                          origin_iata: str,
                          destination_iata: str,
                          departure_date: str,
                          return_date: str = None,
                          adults: int = 1) -> list[dict]:
        """
        Retrieve the best flight offer based on:
        1) Direct flights only (stops = 0), cheapest price.
        2) If no direct, flights with max 1 stop, cheapest price.
        3) Otherwise, option with fewest stops and cheapest price among those.
        """
        offers = await self.search_flight_offers(
            origin_iata, destination_iata, departure_date, return_date, adults
        )
        if not offers:
            return []

        # Map IATA codes to city IDs
        origin_airport = Airport.query.filter_by(iata_code=origin_iata).first()
        if not origin_airport:
            raise LookupError(f"No airport found with IATA code '{origin_iata}'. Please load airport data first.")
        dest_airport = Airport.query.filter_by(iata_code=destination_iata).first()
        if not dest_airport:
            raise LookupError(f"No airport found with IATA code '{destination_iata}'. Please load airport data first.")
        print(f"Found {len(offers)} offers for {origin_iata} to {destination_iata}")

        # Annotate each offer with number of stops and price
        enriched = []
        for o in offers:
            price = float(o['price']['total'])
            segments = o['itineraries'][0]['segments']
            stops = len(segments) - 1
            enriched.append({'offer': o, 'price': price, 'stops': stops})

        # 1) Filter for direct flights
        direct_flights = [e for e in enriched if e['stops'] == 0]
        if direct_flights:
            chosen = min(direct_flights, key=lambda e: e['price'])
        else:
            # 2) Filter for flights with at most 1 stop
            one_stop = [e for e in enriched if e['stops'] <= 1]
            if one_stop:
                chosen = min(one_stop, key=lambda e: e['price'])
            else:
                # 3) Find fewest stops among all, then cheapest
                min_stops = min(e['stops'] for e in enriched)
                fewest = [e for e in enriched if e['stops'] == min_stops]
                chosen = min(fewest, key=lambda e: e['price'])

        o = chosen['offer']
        total_price = chosen['price']
        currency = o['price']['currency']
        stops = chosen['stops']

        entry = {
            'origin_city_id':      origin_airport.city_id,
            'destination_city_id': dest_airport.city_id,
            'departure_date':      departure_date,
            'return_date':         return_date,
            'adults':              adults,
            'max_price_filter':    None,
            'currency_code':       currency,
            'best_price':          total_price,
            'stops_allowed':       stops,
            'fetched_at':          datetime.utcnow()
        }
        return [entry]

    def save_temp_prices(self, entries: list[dict]) -> None:
        """
        Save a list of price dicts into the flight_prices table as temporary entries.
        """
        for data in entries:
            fp = FlightPrice(
                origin_city_id      = data['origin_city_id'],
                destination_city_id = data['destination_city_id'],
                departure_date      = data['departure_date'],
                return_date         = data['return_date'],
                adults              = data['adults'],
                max_price_filter    = data['max_price_filter'],
                currency_code       = data['currency_code'],
                best_price          = data['best_price'],
                stops_allowed       = data['stops_allowed'],
                fetched_at          = data['fetched_at']
            )
            db.session.add(fp)
        db.session.commit()
