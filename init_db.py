# init_db.py
from app import db, app  # Import your app and database

# Create tables within the application context
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
