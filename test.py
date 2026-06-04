from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['excel_to_mongodb_db']
collection = db['imported_data']

count = collection.count_documents({})
print(f"Total records: {count}")

print("\nFirst record:")
print(collection.find_one())

client.close()