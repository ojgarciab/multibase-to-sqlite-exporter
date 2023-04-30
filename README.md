# Multibase/Cosmos export tool to SQLite

The aim of this tool is to export data stored in a Multibase database to a SQLite database to facilitate its access and use by any open-source tool.

To achieve the goal of developing this tool, the following milestones will be followed:

- Read the data stored in the system tables (such as `systables.dat`,`syscolumns.dat`, ect) to understand the database content.
- Analyse the structure of user tables (number of fields, their type and size, ect).
- Generate SQL code by converting Multibase data types to types compatible with SQLite.
- Read the records of each table in the database to export them to the SQLite database.

# Explanation of file structure

All database files are stored in a directory with the `.dbs` extension. 

Inside this directory, a series of system files are created, which start with `sys*` and contain tables with system information:

- `syscolattr.dat`
- `syscolauth.dat`
- `syscollati.dat`
- `syscolumns.dat`
- `sysdepend.dat`
- `sysforeign.dat`
- `sysindexes.dat`
- `sysremote.dat`
- `syssynonym.dat`
- `systabauth.dat`
- `systables.dat`
- `sysusers.dat`
- `sysviews.dat`

The files that contain table data have the extension `*.dat`, and for each table, a file with the extension `*.idx` is created that contains indexed table content information. It is beyond the scope of this tool to interpret index files.

# Current state of the tool

- [x] Loading of table information stored in the `systables.dat` file.
- [x] Loading of field information stored in the `syscolumns.dat` file.
- [ ] Loading of data from `*.dat` tables.
- [ ] Data export.