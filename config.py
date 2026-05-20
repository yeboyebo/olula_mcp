import os

from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("API_HOST", "http://localhost:5000")
API_KEY = os.getenv("API_KEY")