import subprocess

import pymongo

server_name = "photos"
database = "name"
collection = "photos"
shard_key = "name"

# Enables sharding on the database. The prereq being that mongodb is already installed
def temp(config_port = 27019, ):
    # Starting config server
    subprocess.run(f"mongod –configdb ConfServer: {config_port}", shell=True, capture_output=True, text=True)

    # Starting mongos server
    subprocess.run(f"mongos –configdb ConfServer: {config_port}", shell=True, capture_output=True, text=True)

    # Connect to mongos instance and enable sharding for collection
    subprocess.run(f"mongo –host ConfServer –port {config_port}\nsh.shardCollection(\"{database}.{collection}\", { {shard_key} : \"hashed\" })", shell=True, capture_output=True, text=True)

# sh.shardCollection("{database}.{collection}", { {shard_key} : "hashed" })

def create_collection(db_name, collection_name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]

def setup_sharding():
    pass