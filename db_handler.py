from pymongo import MongoClient, errors
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBHandler:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        try:
            self.client = MongoClient(self.config.MONGODB_URI)
            self.client.admin.command('ping')
            self.db = self.client[self.config.DATABASE_NAME]
            self.collection = self.db[self.config.COLLECTION_NAME]
            print("   Connected to MongoDB")
            return True
        except Exception as e:
            print(f"   MongoDB connection failed: {e}")
            return False
    
    def create_schema(self):
        schema = {
            '$jsonSchema': {
                'bsonType': 'object',
                'properties': {
                    'date': {'bsonType': 'string'},
                    'stock': {'bsonType': 'string'},
                    'final_sentiment': {'bsonType': 'double'}
                }
            }
        }
        
        try:
            if self.config.COLLECTION_NAME not in self.db.list_collection_names():
                self.db.create_collection(self.config.COLLECTION_NAME, validator=schema)
                print("   Created collection with schema validation")
        except Exception as e:
            print(f"   Schema creation skipped: {e}")
    
    def insert_many(self, records):
        total_inserted = 0
        
        for i in range(0, len(records), self.config.BATCH_SIZE):
            batch = records[i:i+self.config.BATCH_SIZE]
            try:
                result = self.collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                print(f"   Batch {i//self.config.BATCH_SIZE + 1}: Inserted {len(result.inserted_ids)}")
            except errors.BulkWriteError as e:
                inserted = len(batch) - len(e.details['writeErrors'])
                total_inserted += inserted
                print(f"   Batch {i//self.config.BATCH_SIZE + 1}: Inserted {inserted}, Failed {len(e.details['writeErrors'])}")
        
        return total_inserted
    
    def create_indexes(self):
        self.collection.create_index('date')
        self.collection.create_index('stock')
        self.collection.create_index([('stock', 1), ('date', -1)])
        print("   Created indexes on date and stock")
    
    def get_count(self):
        return self.collection.count_documents({})
    
    def get_sample(self, limit=1):
        return list(self.collection.find().limit(limit))
    
    def close(self):
        if self.client:
            self.client.close()
            print("  Connection closed")