import os

from dotenv import load_dotenv

load_dotenv()
API_KEYS_ENV = os.getenv("API_KEYS")
if not API_KEYS_ENV:
    API_KEYS_ENV = "default_api_key"
API_KEYS = [key.strip() for key in API_KEYS_ENV.split(",") if key.strip()]
if not API_KEYS:
    raise RuntimeError("API_KEYS environment variable is not set.")
