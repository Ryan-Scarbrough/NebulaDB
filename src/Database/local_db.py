import time
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import os
import subprocess

# User variables
db_name = 'nebuladb'
coll_name = 'photos'
shard_key = {'_id': 1}
port = 27017
host = "127.0.0.1"
database_path = "/System/Volumes/Data/data/db"
client = MongoClient(f'mongodb://{host}:{port}')


def start_command():
    # Start MongoDB process in the background
    command = [
        "sudo",
        "mongod",
        "--configsvr",
        "--replSet", "confServer",
        "--dbpath", database_path,
        "--bind_ip", host,
        "--port", str(port)
    ]
    return subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop_command(process):
    time.sleep(5)
    process.terminate()
    process.wait()
    print("MongoDB has been closed")


def send_command(command):
    mongosh_cmd = ["mongosh", "--host", host, "--port", str(port)]
    mongosh_process = subprocess.Popen(mongosh_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
    mongosh_process.stdin.write(command + "\n")
    mongosh_process.stdin.flush()


# TODO: make better way to prevent init twice: if (rs.status().codeName == "NotYetInitialized") rs.initiate()
def start_mongo():
    if not os.path.exists(database_path):
        os.system(f"sudo mkdir -p {database_path}")
        os.system(f"sudo chown -R $(id -un) {database_path}")

    mongo_server = start_command()

    # Initialize the replica set
    send_command("rs.initiate()")
    print("MongoDB has been started!")


# Enable sharding for the database
def enable_sharding(db_name):
    try:
        client.admin.command('enableSharding', db_name)
        print(f"Sharding enabled for database: {db_name}")
    except OperationFailure as e:
        print(f"Error enabling sharding: {e}")


# Create a sharded collection
def create_sharded_collection(db_name, coll_name, shard_key):
    try:
        client[db_name].create_collection(coll_name)
        client.admin.command('shardCollection', f"{db_name}.{coll_name}", key=shard_key)
        print(f"Sharded collection created: {db_name}.{coll_name} with shard key {shard_key}")
    except OperationFailure as e:
        print(f"Error creating sharded collection: {e}")


# Add a new shard
def add_shard(shard_uri):
    try:
        client.admin.command('addShard', shard_uri)
        print(f"Shard added: {shard_uri}")
    except OperationFailure as e:
        print(f"Error adding shard: {e}")


start_mongo()
# enable_sharding(db_name)  # Enable sharding on the database
# create_sharded_collection(db_name, coll_name, shard_key)  # Create a sharded collection
#
# # add_shard('mongodb://localhost:27017')
#
# # Verify shards
# shards = client.admin.command('listShards')
# print("Current shards:", shards)
