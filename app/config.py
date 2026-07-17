import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cases.db")
    USCIS_API_URL = os.getenv("USCIS_API_URL", "https://egov.uscis.gov/casestatus/mycasestatus.do")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
