# Author: Akele Benjamin
from flask_sqlalchemy import SQLAlchemy
from .. import db


db = SQLAlchemy()
from datetime import datetime
# Import all models to register with SQLAlchemy
from app.models.user import User
from app.models.activity import Activity
from app.models.country import Country
from app.models.city import City
from app.models.airport import Airport
from app.models.amenity import Amenity
from app.models.user_preference import UserPreference
from app.models.user_amenity_preference import UserAmenityPreference
from app.models.user_activity_preferences import UserActivityPreference
from app.models.visa_policy import VisaPolicy
from app.models.flight_price import FlightPrice
from app.models.hotel import Hotel
from app.models.recommendation import Recommendation
from app.models.destination import Destination
from app.models.hotel_amentity import hotel_amenities
from app.models.categories import Category


