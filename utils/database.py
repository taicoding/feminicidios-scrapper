import os
from mongoengine import connect


def initialize_database():

    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME")
    connect(db=db_name, host=mongo_uri)
