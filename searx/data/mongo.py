from pymongo import MongoClient
from searx import logger
logger = logger.getChild('mongo')

def insert_to_collection(collection_name, json_document):
    logger.debug(json_document)
    client = MongoClient('localhost', 27017)
    searx_database = client.searx
    collection = searx_database[collection_name]
    return collection.insert(json_document)

