""" Destination Controller for handling destination-related routes. """

__author__ = "Akele Benjamin(620130803)"
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from sqlalchemy import or_
from math import ceil

from .. import db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.airport import Airport
from app.models.visa_policy import VisaPolicy
from app.models.country import Country
from app.models.city import City
from app.models.hotel import Hotel
from app.models.activity import Activity
from app.models.flight_price import FlightPrice
from app.services.hotel_api_service import HotelAPIService
from app.services.reccommendation_service import RecommendationService


dest_bp = Blueprint('destinations', __name__, url_prefix='/destinations')
rec_service = RecommendationService()


async def _fetch_items(pref, page, filters):
    """
    Internal helper to build a paginated list of destination items.
    Returns a tuple: (list_of_items_for_page, total_pages)
    """
    total_weights = rec_service.sum_user_preference_weights(pref.user_id)
    budget = float(pref.budget or 0)
    check_in = pref.check_in_date
    check_out = pref.check_out_date
    num_travelers = pref.number_of_travelers or 1

    visa_filter, in_budget, passport_ok, sort_by, search = filters

    #Select eligible countries
    if visa_filter == 'required':
        origin_id = pref.passport_country_id
        q = (db.session
             .query(VisaPolicy.destination_id)
             .filter_by(origin_id=origin_id, visa_required=True))
        country_ids = [row.destination_id for row in q]
        countries = Country.query.filter(Country.id.in_(country_ids)).all()
    else:
        countries = (
            db.session.query(Country)
            .join(Country.cities)
            .join(City.airports)
            .filter(Airport.iata_code.isnot(None))
            .distinct()
            .all()
        )

    # Build item list
    items = []
    user = User.query.get(pref.user_id)
    origin_airport = Airport.query.filter_by(name=user.port_of_origin).first()
    origin_iata = origin_airport.iata_code if origin_airport else None

    for country in countries:
        for city in country.cities:
            # find a valid airport for the destination city
            airport_dest = next((a for a in city.airports if a.iata_code), None)
            if not airport_dest:
                continue

            # flight cost via RecommendationService
            fp = await rec_service.recommend_flight(
                origin_iata=origin_iata,
                destination_iata=airport_dest.iata_code,
                departure_date=check_in,
                return_date=check_out,
                adults=num_travelers
            )
            flight_cost = float(fp.best_price) if fp else 0.0

            # hotel cost (cheapest)
            hotel = (Hotel.query
                     .filter_by(city_id=city.id)
                     .order_by(Hotel.price)
                     .first())
            hotel_cost = (
                HotelAPIService().generate_price(
                    hotel.rating,
                    num_travelers,
                    [a.name for a in hotel.amenities],
                    check_in,
                    check_out
                ) if hotel else 0.0
            )

            # activity cost sum
            activity_cost = sum(float(a.price or 0) for a in city.activities)

            # compute match score
            score = rec_service.calculate_score(
                sum_of_weights=total_weights,
                budget=budget,
                flight_cost=flight_cost,
                hotel_cost=hotel_cost,
                activity_cost=activity_cost
            )

            # apply filters
            if in_budget and (flight_cost + hotel_cost + activity_cost) > budget:
                continue
            if passport_ok:
                policy = VisaPolicy.query.filter_by(
                    origin_id=pref.passport_country_id,
                    destination_id=country.id
                ).first()
                if policy and not policy.visa_free:
                    continue
            if search and search.lower() not in city.name.lower():
                continue

            items.append({
                'country': country.name,
                'city': city.name,
                'score': round(score, 1),
                'image_url': url_for('static', filename='img/placeholder.jpg')
            })

    # Sort results
    if sort_by == 'distance':
        items.sort(key=lambda it: it.get('distance', float('inf')))
    else:
        items.sort(key=lambda it: it['score'], reverse=True)

    # Paginate
    per_page = 3
    total = len(items)
    pages = ceil(total / per_page)
    start = (page - 1) * per_page
    return items[start:start + per_page], pages


@dest_bp.route('/', methods=['GET'])
async def list_destinations():
    """Render the Destinations page with first-page items."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view destinations.', 'error')
        return redirect(url_for('auth.login'))

    pref = UserPreference.query.get(user_id)
    filters = (
        request.args.get('visa', 'free'),
        request.args.get('in_budget') == 'on',
        request.args.get('available_to_passport') == 'on',
        request.args.get('sort_by', 'score'),
        request.args.get('search', '').strip()
    )
    page = request.args.get('page', 1, type=int)

    items, pages = await _fetch_items(pref, page, filters)

    return render_template(
        'destinations.html',
        items=items,
        page=page,
        pages=pages,
        visa_filter=filters[0],
        in_budget=filters[1],
        passport_ok=filters[2],
        sort_by=filters[3],
        search=filters[4]
    )


@dest_bp.route('/api', methods=['GET'])
async def api_destinations():
    """JSON endpoint for loading additional destination pages asynchronously."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Please log in.'}), 401

    pref = UserPreference.query.get(user_id)
    filters = (
        request.args.get('visa', 'free'),
        request.args.get('in_budget') == 'on',
        request.args.get('available_to_passport') == 'on',
        request.args.get('sort_by', 'score'),
        request.args.get('search', '').strip()
    )
    page = request.args.get('page', 1, type=int)

    items, pages = await _fetch_items(pref, page, filters)
    return jsonify({'items': items, 'page': page, 'pages': pages})


@dest_bp.route('/<int:country_id>/<int:city_id>')
def details(country_id: int, city_id: int):
    """Show detailed view for a specific destination."""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view destination details.', 'error')
        return redirect(url_for('auth.login'))

    country = Country.query.get(country_id)
    city = City.query.get(city_id)
    if not country or not city or city.country_id != country_id:
        flash('Destination not found.', 'error')
        return redirect(url_for('destinations.list_destinations'))

    pref = rec_service.get_user_preference(user_id)
    total_weights = rec_service.sum_user_preference_weights(user_id)
    budget = float(pref.budget or 0)
    check_in = pref.check_in_date
    check_out = pref.check_out_date
    num_travelers = pref.number_of_travelers or 1

    # Flight cost
    fp = rec_service.recommend_flight(
        origin_iata=pref.passport_country.iso_code,
        destination_iata=city.name,
        departure_date=check_in,
        return_date=check_out,
        adults=num_travelers
    )
    flight_cost = float(fp.best_price) if fp else 0.0

    # Activities & costs
    activities = Activity.query.filter_by(city_id=city.id).all()
    activity_cost = sum(float(a.price or 0) for a in activities)

    # Hotel cost (cheapest)
    hotel_cost = (
        db.session.query(db.func.min(FlightPrice.best_price))
        .filter(FlightPrice.destination_city_id == city_id)
        .scalar() or 0.0
    )

    # Compute % score
    score = rec_service.calculate_score(
        sum_of_weights=total_weights,
        budget=budget,
        flight_cost=flight_cost,
        hotel_cost=hotel_cost,
        activity_cost=activity_cost
    )

    return render_template(
        'destination_details.html',
        country=country,
        city=city,
        activities=activities,
        flight_cost=flight_cost,
        score=round(score, 1)
    )
