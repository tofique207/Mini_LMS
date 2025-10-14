import os
from dotenv import load_dotenv

load_dotenv()  # loads values from .env

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqldb://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
