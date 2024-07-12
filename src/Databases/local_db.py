import time
from pathlib import Path
import os
from datetime import datetime
from pymongo import MongoClient
from bson.son import SON
from pymongo.errors import OperationFailure, ConnectionFailure
import socket

mongo_log_dir = Path.cwd().parent.parent / 'logs' / 'mongo'
project_home = Path.cwd().parent.parent


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
        except OSError:
            return True
        return False


def ping_port(host, port, timeout=5):
    start_time = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            end_time = time.time()
            return end_time - start_time
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None


# Having a space in file names messes stuff up
def fix_path(path):
    path = str(path)
    return path.replace(" ", "\\ ")


# This is just a mixin class so that code can be reused and not be redundant copy-paste
class ServerMixin:
    @property
    def host(self):
        raise NotImplementedError("Subclasses should define host")

    @property
    def port(self):
        raise NotImplementedError("Subclasses should define port")

    @property
    def repl(self):
        raise NotImplementedError("Subclasses should define repl")

    @property
    def directory(self):
        raise NotImplementedError("Subclasses should define directory")

    @property
    def path(self):
        raise NotImplementedError("Subclasses should define path")

    @property
    def server_type(self):
        raise NotImplementedError("Subclasses should define server_type")

    def is_open(self):
        response = ping_port(self.host, self.port)
        return False if response is None else True

    def start(self):
        if self.is_open():
            print("Server is already started. Ignoring start command")
            return

        now = str(datetime.now().strftime("%Y%m%d_%H%M%S")) + ".log"
        os.system(
            f"nohup mongod --{self.server_type} --port {self.port} --bind_ip {self.host} --replSet {self.repl} --dbpath {self.path} > {fix_path(mongo_log_dir / self.directory / now)} &")

    def stop(self):
        # Its probably fine
        try:
            mongo_socket = MongoClient(self.host, self.port, directConnection=True)
            db = mongo_socket.admin
            db.command('shutdown')
        except:
            pass

    def configure(self):
        if not self.is_open():
            print("Server is not open. Starting...")
            self.start()
            time.sleep(1)  # wait for server to start

        # Mongos does not need configuration in the same way the other servers do
        if self.server_type == 'mongos':
            print("Mongos server does not require direct configuration")
            return

        mongo_socket = MongoClient(self.host, self.port, directConnection=True)
        db = mongo_socket.admin

        try:
            db.command(SON([('replSetGetStatus', 1)]))  # check if the server is already configured
            print("Server is already configured. Ignoring command")
        except OperationFailure:
            # Continue with configuration if not already configured
            rsconf = {"_id": self.repl, "members": [{"_id": 0, "host": f"{self.host}:{self.port}"}]}
            try:
                result = db.command("replSetInitiate", rsconf)
                print("Replica set initiated successfully:", result)
            except Exception as e:
                print("Error initiating replica set:", e)

        mongo_socket.close()


class Config(ServerMixin):
    port = 27020
    host = 'localhost'
    repl = 'config_repl'
    directory = 'config'
    path = project_home / 'config' / 'mongo' / directory
    path = fix_path(path)
    server_type = 'configsvr'


class ShardOne(ServerMixin):
    port = 28021
    host = 'localhost'
    repl = 'shard1_repl'
    directory = 'shard1'
    path = project_home / 'config' / 'mongo' / directory
    path = fix_path(path)
    server_type = 'shardsvr'


class Mongos(ServerMixin):
    port = 29000
    host = 'localhost'
    repl = 'config_repl'
    directory = 'mongos'
    path = project_home / 'config' / 'mongo' / directory
    path = fix_path(path)
    server_type = 'mongos'

    def start(self):
        if self.is_open():
            print("Server is already started. Ignoring start command")
            return

        now = str(datetime.now().strftime("%Y%m%d_%H%M%S")) + ".log"
        os.system(
            f"nohup mongos --configdb {Config.repl}/{Config.host}:{Config.port} --bind_ip {self.host} --port {self.port} > {fix_path(mongo_log_dir / self.directory / now)} &")


def _make_dir_helper(directories: list, parent_directory):
    os.chdir(parent_directory)
    for d in directories:
        try:
            os.makedirs(d)
        except FileExistsError:
            print(f"Directory {d} already exists. Skipping creation")


# Making the folders for all the servers
def make_directories():
    try:
        os.chdir(project_home / 'config')
        os.makedirs('mongo')
    except FileExistsError:
        print(f"Directory config/mongo already exists. Skipping creation")

    try:
        os.chdir(project_home / 'logs')
        os.makedirs('mongo')
    except FileExistsError:
        print(f"Directory logs/mongo already exists. Skipping creation")

    # If another directory is added, make sure Mongos is the last one
    directory_names = [Config.directory, ShardOne.directory, Mongos.directory]

    mongo_servers = project_home / 'config' / 'mongo'
    _make_dir_helper(directory_names[:-1], mongo_servers)

    mongo_logs = project_home / 'logs' / 'mongo'
    _make_dir_helper(directory_names, mongo_logs)


# Should be passed a path for the first shard chosen by the user
def initialize(path: str):
    make_directories()
    Config().configure()
    first_shard = ShardOne()
    first_shard.path = path
    first_shard.configure()
    Mongos().configure()


def start():
    Config().start()
    ShardOne().start()
    Mongos().start()


def stop():
    Mongos().stop()
    ShardOne().stop()
    Config().stop()
