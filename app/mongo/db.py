from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["adm_new_project"]

def get_mongo_db():
    return db
