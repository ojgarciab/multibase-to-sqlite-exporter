# Multibase/Cosmos export tool to SQLite

The aim of this tool is to export data stored in a Multibase database to a SQLite database to facilitate its access and use by any open-source tool.

To achieve the goal of developing this tool, the following milestones will be followed:

- Read the data stored in the system tables (such as `systables.dat`,`syscolumns.dat`, ect) to understand the database content.
- Analyse the structure of user tables (number of fields, their type and size, ect).
- Generate SQL code by converting Multibase data types to types compatible with SQLite.
- Read the records of each table in the database to export them to the SQLite database.