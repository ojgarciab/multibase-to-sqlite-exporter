""" Checks for library functionality """

import argparse
from multibase import MultibaseReader

parser = argparse.ArgumentParser(description="Checks for library functionality",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("path", help="Path to the '.dbs' directory")
args = parser.parse_args()
config = vars(args)

database = MultibaseReader(config["path"])

print(database.get_tables())
