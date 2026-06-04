import os
from pathlib import Path

class Config:
    # File paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    INPUT_FILE = DATA_DIR / 'news_features.csv'
    MONGODB_URI = 'mongodb://localhost:27017/'
    DATABASE_NAME = 'excel_to_mongodb_db'
    COLLECTION_NAME = 'imported_data'
    BATCH_SIZE = 1000
    REQUIRED_COLUMNS = ['date', 'stock', 'final_sentiment']
    SENTIMENT_MIN = -1
    SENTIMENT_MAX = 1