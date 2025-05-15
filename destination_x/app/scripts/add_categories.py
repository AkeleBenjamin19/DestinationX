""" This script:
Add categories to the database from Activity.category field
This script fetches distinct category names from the Activity model
and inserts them into the Category model if they do not already exist."""


__author__ = "Akele Benjamin(620130803)"
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

top = Path(__file__).parents[2]
sys.path.insert(0, str(top))

from app import create_app, db
from app.models.activity import Activity
from app.models.categories import Category

    
def main():
    load_dotenv(top / ".env")
    app = create_app()
    return app

if __name__ == '__main__':
    app = main()
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
