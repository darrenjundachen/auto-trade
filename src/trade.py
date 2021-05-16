from tinydb import TinyDB, Query

config_db = TinyDB("../config-db.json")
config = config_db.all()[0]

