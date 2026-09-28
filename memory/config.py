import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
    HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "precedent-aml")
    HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

config = Config()
