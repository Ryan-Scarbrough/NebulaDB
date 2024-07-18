import inspect
import json
import time
from json import JSONDecodeError
from pathlib import Path
import os
from datetime import datetime
from pymongo import MongoClient
from bson.son import SON
from pymongo.errors import OperationFailure, ConnectionFailure
import socket


class FindMe:
    pass


class_file_path = Path(inspect.getfile(FindMe)).resolve()
project_home = class_file_path.parent.parent.parent
mongo_log_dir = project_home / 'logs' / 'mongo'
json_file_path = project_home / 'config' / 'databases.json'


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
        log_path = mongo_log_dir / self.directory / now
        os.system(
            f"nohup mongod --{self.server_type} --port {self.port} --bind_ip {self.host} --replSet {self.repl} --dbpath {self.path} > {log_path} &")

    def stop(self):
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
            time.sleep(1)

        if self.server_type == 'mongos':
            print("Mongos server does not require direct configuration")
            return

        mongo_socket = MongoClient(self.host, self.port, directConnection=True)
        db = mongo_socket.admin

        try:
            db.command(SON([('replSetGetStatus', 1)]))
            print("Server is already configured. Ignoring command")
        except OperationFailure:
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
    server_type = 'configsvr'


class ShardOne(ServerMixin):
    port = 28021
    host = 'localhost'
    repl = 'shard1_repl'
    directory = 'shard1'
    path = None
    server_type = 'shardsvr'


class Mongos(ServerMixin):
    port = 29000
    host = 'localhost'
    repl = 'config_repl'
    directory = 'mongos'
    path = project_home / 'config' / 'mongo' / directory
    server_type = 'mongos'

    def start(self):
        if self.is_open():
            print("Server is already started. Ignoring start command")
            return

        now = str(datetime.now().strftime("%Y%m%d_%H%M%S")) + ".log"
        log_path = mongo_log_dir / self.directory / now
        os.system(
            f"nohup mongos --configdb {Config.repl}/{Config.host}:{Config.port} --bind_ip {self.host} --port {self.port} > {log_path} &")


def _make_dir_helper(directories: list, parent_directory):
    parent_directory.mkdir(parents=True, exist_ok=True)
    for d in directories:
        (parent_directory / d).mkdir(parents=True, exist_ok=True)


def make_directories():
    (project_home / 'config' / 'mongo').mkdir(parents=True, exist_ok=True)
    (project_home / 'logs' / 'mongo').mkdir(parents=True, exist_ok=True)

    directory_names = [Config.directory, Mongos.directory]
    mongo_servers = project_home / 'config' / 'mongo'
    _make_dir_helper(directory_names[:-1], mongo_servers)

    mongo_logs = project_home / 'logs' / 'mongo'
    _make_dir_helper(directory_names, mongo_logs)


def json_init(first_shard):
    config_json = {
        "type": "config",
        "path": str(Config.path),
        "port": Config.port,
        "host": Config.host
    }

    mongos_json = {
        "type": "mongos",
        "path": str(Mongos.path),
        "port": Mongos.port,
        "host": Mongos.host
    }

    shard_json = {
        "shard_index": 1,
        "name": "Database 1",
        "path": str(first_shard.path),
        "port": ShardOne.port,
        "host": ShardOne.host
    }

    try:
        with open(json_file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
            except JSONDecodeError:
                data = {}
    except FileNotFoundError:
        print("Database .json not found. Creating one")
        data = {}

    try:
        if 'local' in data or isinstance(data['local'], list):
            return
    except KeyError:
        pass

    data['local'] = {}
    data['local']['config'] = config_json
    data['local']['mongos'] = mongos_json
    data['local']['shards'] = []
    data['local']['shards'].append(shard_json)

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def should_init() -> bool:
    try:
        with open(json_file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
            except JSONDecodeError:
                return True
            if "Local" in data and isinstance(data["Local"], list):
                return False
            else:
                return True
    except FileNotFoundError:
        return True


def initialize(path: str) -> bool:
    if not should_init():
        print("Initialization already complete. Skipping")
        return False

    make_directories()
    Config().configure()
    first_shard = ShardOne()
    first_shard.path = Path(path).resolve()
    first_shard.configure()
    Mongos().configure()
    json_init(first_shard)
    return True


def start():
    Config().start()
    ShardOne().start()
    Mongos().start()


def stop():
    Mongos().stop()
    ShardOne().stop()
    Config().stop()
