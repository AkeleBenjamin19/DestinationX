# DestinationX Travel Recommender

DestinationX is a Flask-based travel recommendation engine that
suggests destinations, flights, hotels, and activities based on user
preferences.

## Features
- User signup/login, preferences wizard
- Flight pricing via Amadeus API
- Hotel dynamic pricing 
- Visa policy scraping & storage
- Category-based activity recommendations

## Quickstart
Create the database called destination_x in POSTGRESQL.

Modify link in .env to update user and password.


```bash
# Clone & install
git clone https://github.com/AkeleBenjamin19/DestinationX.git
cd destinationx
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set environment
export FLASK_APP=app
export FLASK_ENV=development
export SECRET_KEY='your-secret-key'
export DATABASE_URL=postgresql://user:pass@localhost/destx

# Initialize DB
flask intial db init
flask migrate "name migration"
flask db upgrade
python app/scripts/import_countries.py
python app/scripts/import_all_visas.py
python app/scripts/import_cities.py
python app/scripts/import_categories.py
python app/scripts/add_iata_code.py
python app/scripts/import_airports.py
python app/scripts/import_activities.py
python app/scripts/import_hotels.py
python app/scripts/add_categories.py

# Run 
pyhton run,py
