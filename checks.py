""" Checks for library functionality """

import argparse
import json
from multibase import MultibaseReader

parser = argparse.ArgumentParser(
    description="Checks for library functionality",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("path", help="Path to the '.dbs' directory")
parser.add_argument("database", help="Dump database data")
parser.add_argument("--schema", action="store_true", default=False,
                    help="Include schema dump")
args = parser.parse_args()
config = vars(args)

database = MultibaseReader(config["path"])

if config["schema"]:
    print(json.dumps(database.schema[config["database"]], indent=4))
print(json.dumps(database.read_table(config["database"]), indent=4))
