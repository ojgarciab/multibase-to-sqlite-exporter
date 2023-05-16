""" Checks for library functionality """

import argparse
import json
from multibase import MultibaseReader

parser = argparse.ArgumentParser(
    description="Checks for library functionality",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("path", help="Path to the '.dbs' directory")
args = parser.parse_args()
config = vars(args)

database = MultibaseReader(config["path"])

# Export database schema
print(json.dumps(database.schema, indent=4))
# Export the contents of the last table in the schema
print(json.dumps(database.read_table(next(reversed(database.schema))), indent=4))
