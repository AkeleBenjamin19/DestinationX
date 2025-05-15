"""Recommendation Service Module
This module contains the RecommendationService class which is responsible for
providing travel recommendations based on user preferences and available
destinations.
It includes methods for fetching available destinations, local options,
flight recommendations, hotel pricing, and calculating scores based on user
preferences."""

__author__ = "Akele Benjamin(620130803)"
from datetime import date, datetime
from typing import Optional, Union, List, Dict
from sqlalchemy import or_
from .. import db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.country import Country
from app.models.city import City
from app.models.hotel import Hotel
from app.models.activity import Activity
from app.models.flight_price import FlightPrice
from app.models.visa_policy import VisaPolicy
from app.services.flight_api_service import FlightAPIService
from app.services.hotel_api_service import HotelAPIService

class RecommendationService:
    """
    Provides travel recommendations: available destination countries,
    detailed destinations, local hotels and activities, flight options,
    hotel pricing, and user preference analysis.
    """
    def __init__(self):
        self.flight_service = FlightAPIService()
        self.hotel_service  = HotelAPIService()

    def get_available_destinations(self) -> List[Country]:
        """
        Return all countries where the visa policy allows at least one of:
        visa_free or visa_on_arrival.
        """
        destinations = (
            Country.query
            .join(VisaPolicy, Country.id == VisaPolicy.destination_id)
            .filter(
                or_(
                    VisaPolicy.visa_free.is_(True),
                    VisaPolicy.visa_on_arrival.is_(True)
                )
            )
            .all()
        )
        return destinations

    def get_all_destinations(self) -> List[Country]:
        """
        Return all countries in the database.
        """
        return Country.query.all()

    def get_destinations(self, countries: List[Country]) -> Dict[int, Dict[str, object]]:
        """
        Given a list of Country objects, return for each country:
          - the Country object
          - a list of its cities, each with associated activities
        Result format:
        {
          country_id: {
            'country': Country,
            'cities': [
              {'city': City, 'activities': List[Activity]},
              ...
            ]
          },
          ...
        }
        """
        result: Dict[int, Dict[str, object]] = {}
        for country in countries:
            if not country:
                continue
            cid = country.id
            city_objs = City.query.filter_by(country_id=cid).all()
            city_list = []
            for city in city_objs:
                activities = Activity.query.filter_by(city_id=city.id).all()
                city_list.append({'city': city, 'activities': activities})
            result[cid] = {'country': country, 'cities': city_list}
        return result

    def get_local_options(self, country_id: int) -> dict:
        """
        Given a destination country ID, select its first city,
        then return lists of hotels and activities in that city.
        """
        country = Country.query.get(country_id)
        if not country:
            raise ValueError(f"Country id={country_id} not found")

        city = City.query.filter_by(country_id=country.id).first()
        if not city:
            return {'hotels': [], 'activities': []}

        hotels = Hotel.query.filter_by(city_id=city.id).all()
        activities = Activity.query.filter_by(city_id=city.id).all()
        return {'hotels': hotels, 'activities': activities}

    def recommend_flight(
        self,
        origin_iata: str,
        destination_iata: str,
        departure_date: Union[str, date],
        return_date: Optional[Union[str, date]] = None,
        adults: int = 1
    ) -> Optional[FlightPrice]:
        """
        Use FlightAPIService to find the best flight offer, save it to DB,
        and return the FlightPrice model instance.
        """
        entries = self.flight_service.get_price_entries(
            origin_iata,
            destination_iata,
            str(departure_date),
            str(return_date) if return_date else None,
            adults
        )
        if not entries:
            return None

        data = entries[0]
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
        return fp

    def calculate_hotel_price(
        self,
        hotel_id: int,
        num_persons: int,
        check_in: Union[str, date, datetime],
        check_out: Union[str, date, datetime]
    ) -> float:
        """
        Compute dynamic price for a hotel stay using HotelAPIService.generate_price.
        """
        hotel = Hotel.query.get(hotel_id)
        if not hotel:
            raise ValueError(f"Hotel id={hotel_id} not found")

        amen_names = [a.name for a in hotel.amenities]
        return self.hotel_service.generate_price(
            hotel.rating,
            num_persons,
            amen_names,
            check_in,
            check_out
        )

    def sum_user_preference_weights(self, user_id: int) -> float:
        """
        Retrieve all weight_* fields from UserPreference for the given user,
        sum them, and return the total.
        """
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            raise ValueError(f"UserPreference for user id={user_id} not found")

        weights = [
            pref.weight_winter_sports,
            pref.weight_advennture,
            pref.weight_outdoor,
            pref.weight_shopping,
            pref.weight_arts,
            pref.weight_road,
            pref.weight_wildlife,
            pref.weight_historical,
            pref.weight_beach,
            pref.weight_food,
            pref.weight_wine,
            pref.weight_education,
            pref.weight_culture,
            pref.weight_wellness,
            pref.weight_family,
            pref.weight_music,
            pref.weight_festival,
            pref.weight_landmarks
        ]
        total = sum(float(w) for w in weights if w is not None)
        return total

    def calculate_score(
        self,
        sum_of_weights: float,
        budget: float,
        flight_cost: float,
        hotel_cost: float,
        activity_cost: float
    ) -> float:
        """
        Calculate an overall recommendation score based on user preferences and costs.
        """
        # Prevent division by zero
        total_cost = flight_cost + hotel_cost + activity_cost
        if total_cost <= 0:
            return 0.0
        budget_ratio = budget / total_cost
        # Assuming total_weight is sum_of_weights (max possible)
        total_weight = sum_of_weights
        percentage_score = (sum_of_weights / total_weight) * budget_ratio * 100
        return percentage_score
