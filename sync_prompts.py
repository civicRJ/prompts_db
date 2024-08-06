import json
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME')

# List of JSON files and corresponding collection names from env
json_files_collections = [
    (os.getenv('JSON_FILE1'), os.getenv('COLLECTION_NAME1')),
    (os.getenv('JSON_FILE2'), os.getenv('COLLECTION_NAME2')),
    (os.getenv('JSON_FILE3'), os.getenv('COLLECTION_NAME3')),
]

# Function to convert documents with $oid to ObjectId
def convert_oid(doc):
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, dict) and '$oid' in value:
                doc[key] = ObjectId(value['$oid'])
            else:
                convert_oid(value)
    elif isinstance(doc, list):
        for item in doc:
            convert_oid(item)
    return doc

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[db_name]

for json_file, collection_name in json_files_collections:
    if json_file and collection_name:
        collection = db[collection_name]

        # Drop the collection to clear existing data
        collection.drop()

        # Read and convert JSON data
        with open(json_file, 'r') as file:
            data = json.load(file)
            data = convert_oid(data)

        # Insert data into collection
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

        print(f"Data imported successfully into {collection_name} from {json_file}!")
    else:
        print(f"Skipping entry due to missing file or collection name.")
