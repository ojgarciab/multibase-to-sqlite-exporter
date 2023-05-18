""" Checks for library functionality """

import argparse
import json
from multibase import MultibaseReader

parser = argparse.ArgumentParser(
    description="Checks for library functionality",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("path", help="Path to the '.dbs' directory")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--list-tables", action="store_true",
                   help="List tables in database")
group.add_argument("--dump-schema", action="store_true",
                   help="Dump schema data")
group.add_argument("--dump-table", metavar="table_name", help="Dump database data")
args = parser.parse_args()
config = vars(args)
database = MultibaseReader(config["path"])

if config["dump_schema"]:
    print(json.dumps(database.schema, indent=4))
elif config["list_tables"]:
    print(json.dumps(list(database.schema.keys()), indent=4))
elif config["dump_table"]:
    print(json.dumps(database.read_table(config["dump_table"]), indent=4))
