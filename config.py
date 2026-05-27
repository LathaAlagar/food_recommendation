import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'foodiefinds_secret_key_default_987654')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'foodiefinds_jwt_key_default_987654')
    
    # Database configuration (support Heroku/Render postgres/mysql URI translation)
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini configurations
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
