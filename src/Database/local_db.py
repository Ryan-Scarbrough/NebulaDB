from pathlib import Path
import os
from datetime import datetime

mongo_log_dir = Path.cwd().parent / 'logs' / 'mongo'


class Config:
    port = 27020
    host = 'localhost'
    repl = 'config_repl'
    directory = 'config'

    def start(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.system(f"mongod --configsvr --port {self.port} --bind_ip {self.host} --replSet {self.repl} --dbpath {self.directory} > {str(mongo_log_dir / self.directory / now)}")


class ShardOne:
    port = 28021
    host = 'localhost'
    repl = 'shard1_repl'
    directory = 'shard1'

    def start(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.system(f"mongod --shardsvr --port {self.port} --bind_ip {self.host} --replSet {self.repl} --dbpath {self.directory} > {str(mongo_log_dir / self.directory / now)}")


class Mongos:
    port = 29000
    host = 'localhost'
    repl = 'config_repl'
    directory = 'mongos'

    def start(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.system(f"mongos --configdb {Config.repl}/{Config.host}:{Config.port} --bind_ip {self.host} --port {self.port} > {str(mongo_log_dir / self.directory / now)}")


def _make_dir_helper(directories: list, parent_directory):
    os.chdir(parent_directory)
    for d in directories:
        try:
            os.makedirs(d)
        except FileExistsError:
            print(f"Directory {d} already exists. Skipping creation")


# Making the folders for all the servers
def make_directories():
    project_home = Path.cwd().parent

    try:
        os.makedirs('mongo')
    except FileExistsError:
        print(f"config/mongo directory already exists. Skipping creation")

    # If another directory is added, make sure Mongos is the last one
    directory_names = [Config.directory, ShardOne.directory, Mongos.directory]

    mongo_servers = project_home / 'config' / 'mongo'
    _make_dir_helper(directory_names[:-1], mongo_servers)

    mongo_logs = project_home / 'logs' / 'mongo'
    _make_dir_helper(directory_names, mongo_logs)







