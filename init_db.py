from app import create_app, db
from app.models import Course

app=create_app()

with app.app_context():
    db.create_all()
    print("ALL Tables Created Successfully!!")