"""
This Python script is a component of the Destination X service.

The script is designed to be run as a Flask web application, 
allowing for easy integration with other components of the 
Destination X service.

It fetches flight prices from the Destination X MySQL 
database with the following parameters:

    - Origin city/location
    - Destinaion city/location
    - Departure date
    - Return date
    - Number of passengers
    - Maximum price
    - Desired currency

It uses the Amadeus API to get flight prices and availability 
based on these criteria and displays them.

Specific flight offers are returned in JSON format, with added filtering
for the following parameters:

    - City to IATA code conversion
    - Sorting my lowest price
    - Filtering by number of stops, with preference to direct flights
      where available. If not, maximum of 1 stop is allowed.


Author:
        Xenique Daize, Member
        Destination X Team
        University of the West Indies, Mona.
        April 2025

"""
# Import necessary libraries
from flask import Flask, jsonify
import mysql.connector
from mysql.connector import * 
from amadeus import *
import os
import json
from datetime import datetime



# Initialize Flask app
app = Flask(__name__)


# Setup Amadeus API client
amadeus = Client(
    client_id='YOUR_AMADEUS_CLIENT_ID',
    client_secret='YOUR_AMADEUS_CLIENT_SECRET'
)


#Setup for MySQL connection
def get_data():
    return mysql.connector.connect(
        host = 'localhost',
        user = 'username',
        password = 'password',
        database = 'database'
    )

# Safeguard function to convert city name into IATA code
def convert_city(city):
    try:
        response = amadeus.reference_data.locations.get(
            keyword= city,
            subType='CITY'
        )
        return response.data[0]['iataCode']
    except Exception as e:
        print(f"Error converting {city} to IATA: {e}")
        return None
    
#Calulate layover time between flights
def calculate_layover_time(segments):
    if len(segments) < 2:
        return 0
    first_arrival = segments[0]['arrival']['at']
    second_departure = segments[1]['departure']['at']
    dt1 = datetime.fromisoformat(first_arrival)
    dt2 = datetime.fromisoformat(second_departure)
    return int((dt2 - dt1).total_seconds() / 60)


# Route to handle flight search requests
@app.route('/search')

#Function to handle flight search requests
def search():

    #Connect to the database
    conn = get_data()
    cursor = conn.cursor(dictionary = True)

    #Fetch the most recent request from the database
    cursor.execute("SELECT * FROM requests ORDER BY id DESC LIMIT 1")
    request = cursor.fetchone()
    conn.close()

    #Check if there are any requests in the database
    #If there are no requests, return a message
    if not request:
        return "No requests found for querying"
    
    #Convert the origin and destination city names to IATA codes
    from_city = convert_city(request['from_city'])
    to_city = convert_city(request['to_city'])

    #Check if the conversion was successful
    #If not, return an error message
    if not from_city or not to_city:
        return "Error converting city names to IATA codes"
    

    #Try to fetch flight offers from Amadeus API
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=from_city,
            destinationLocationCode=to_city,
            departureDate=request['departure_date'],
            returnDate=request['return_date'] if request['return_date'] else None,
            adults=request['passengers'],
            maxPrice=request['max_price'],
            currencyCode=request['currency'],

            #Set max number of results to return
            #This is limited to 3 for testing purposes
            max=3
        )

        #Filter for direct or one-stop flights

        filtered_flights = []
        for flight in response.data:
            if all(len(itin['segments']) <= 2 for itin in flight['itineraries']):

                # Extract duration and layover
                flight_info = {
                    "price": flight['price']['total'],
                    "currency": flight['price']['currency'],
                    "itineraries": []
                }

                # Extracting itinerary details
                for itin in flight['itineraries']:
                    segments = itin['segments']
                    duration = itin['duration']
                    layover = calculate_layover_time(segments)

                    flight_info["itineraries"].append({
                        "duration": duration,
                        "layover_minutes": layover,
                        "segments": [{
                            "from": seg['departure']['iataCode'],
                            "to": seg['arrival']['iataCode'],
                            "departure": seg['departure']['at'],
                            "arrival": seg['arrival']['at'],
                            "carrierCode": seg['carrierCode'],
                            "flightNumber": seg['number']
                        } for seg in segments]
                    })
                filtered_flights.append(flight_info)

        
        #Sort and limit to top 5 by price
        top_flights = sorted(filtered_flights, key=lambda x: float(x['price']) )[:5]
        
        #Save to JSON file
        output_file = 'flight_offers.json'
        output_path = os.path.join(os.getcwd(), output_file)
        with open(output_file, 'w') as f:
            json.dump(top_flights, f, indent=4)

        return jsonify({
            "message": f"Flight offers fetched successfully and saved to {output_file}",
            "status": "success"
        })


    except ResponseError as e:
        print(f"Error fetching flight offers: {e}")
        results = [{"error": "API error"}]
        return jsonify({
            "message": "Error fetching flight offers",
            "status": "error",
            "error": str(e)
        })

