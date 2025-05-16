# Author: Akele Benjamin
# This script adds unique categories to the database from the Activity model.
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# ensure project root on path
top = Path(__file__).parents[2]
sys.path.insert(0, str(top))

from app import create_app, db
from app.models.activity import Activity
from app.models.categories import Category


def main():
    pass
    
def create_app_env():
    load_dotenv(top / ".env")
    app = create_app()
    return app

if __name__ == '__main__':
    app = create_app_env()
    with app.app_context():
        # fetch distinct category names from Activity.category field
        categories = db.session.query(Activity.category).distinct().all()
        names = [c[0] for c in categories if c[0]]
        print(f"Found {len(names)} unique category names.")

        created = 0
        for name in names:
            # skip if already exists
            if not Category.query.filter_by(name=name).first():
                cat = Category(name=name)
                db.session.add(cat)
                created += 1
        db.session.commit()
        print(f"Inserted {created} new Category records.")
