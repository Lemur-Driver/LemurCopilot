import os

from pymongo import AsyncMongoClient


MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["MONGODB_DATABASE"]

client = AsyncMongoClient(MONGODB_URI)
database = client[DATABASE_NAME]