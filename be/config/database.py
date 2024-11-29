from pymongo import MongoClient
import os
from dotenv import load_dotenv
url = os.getenv('MONGO_URL')
client = MongoClient(url)
db = client["P2P"]

def get_db():
    return db

def close_connection():
    # Kiểm tra kết nối đến MongoDB
    try:
        client.server_info()('ping')
        #client.admin.command('ping')
        #db.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Unable to connect to MongoDB: {e}")
        
    # Đóng kết nối MongoDB
    client.close()
