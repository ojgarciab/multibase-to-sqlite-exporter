# Multibase/Cosmos export tool to SQLite

The aim of this tool is to export data stored in a Multibase database to a SQLite database to facilitate its access and use by any open-source tool.

To achieve the goal of developing this tool, the following milestones will be followed:

- Read the data stored in the system tables (such as `systables.dat`,`syscolumns.dat`, ect) to understand the database content.
- Analyse the structure of user tables (number of fields, their type and size, ect).
- Generate SQL code by converting Multibase data types to types compatible with SQLite.
- Read the records of each table in the database to export them to the SQLite database.

# Step-by-step installation

Create the Python virtual environment, activate it, and install dependencies (currently none) by typing the following instructions:

    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt

Uncompress the file containing the contents of the demonstration database and verify the functionality of the library by typing the following instructions:

    tar jxvf mbdemo.tar.bz2
    python3 checks.py mbdemo/almacen.dbs/

# Explanation of file structure

All database files are stored in a directory with the `.dbs` extension. 

Inside this directory, a series of system files are created, which start with `sys*` and contain tables with system information:

| tabid | data file      | index file     |
|-------|----------------|----------------|
| 1     | systables.dat  | systables.idx  |
| 2     | syscolumns.dat | syscolumns.idx |
| 3     | sysindexes.dat | sysindexes.idx |
| 4     | systabauth.dat | systabauth.idx |
| 5     | syscolauth.dat | syscolauth.idx |
| 6     | sysviews.dat   | sysviews.idx   |
| 7     | sysusers.dat   | sysusers.idx   |
| 8     | sysdepend.dat  | sysdepend.idx  |
| 9     | syssynonym.dat | syssynonym.idx |
| 10    | sysforeign.dat | sysforeign.idx |
| 11    | syscolattr.dat | syscolattr.idx |
| 12    | syscollati.dat | syscollati.idx |
| 17    | sysremote.dat  | sysremote.idx  |

The files that contain table data have the extension `*.dat`, and for each table, a file with the extension `*.idx` is created that contains indexed table content information. It is beyond the scope of this tool to interpret index files.

# Current state of the tool

- [x] Loading of table information stored in the `systables.dat` file.
- [x] Loading of field information stored in the `syscolumns.dat` file.
- [ ] Loading of data from `*.dat` tables.
- [ ] Data export.

# File Format
Big-endian byte ordering places the most significant byte first. This method is used in IBM® mainframe processors. `>` indicates that the binary string is in big-endian format (higher-order bytes are stored first).

Data types represented in python's [`unpack()`](https://docs.python.org/3/library/struct.html#format-characters) format¹:

| Code | Name       | Format |
|------|------------|--------|
| 0    | CHAR       | 000s   |
| 1    | SMALLINT   | h/H    |
| 2    | INTEGER    | l/L    |
| 3    | TIME       | L¹     |
| 5    | DECIMAL    | L²     |
| 6    | SERIAL     | L      |
| 7    | DATE       | L¹     |
| >7   | ???        | -³     |

1. Numeric values representing the number of days since 31st December 1899 or the number of seconds since 00:00 AM. Apparently, the first bit of the value represents a null value.
2. Apparently, it is an unsigned number.
3. There may be more data types that have not yet been found and analyzed in the files we have for that purpose.

## `systables.dat`
Currently, the string `">18s8s64sL37s1s"` is used to obtain the information. The format string `">18s8s64sL37s1s"` breaks down as follows:

- `tabname` (`CHAR(18)`): name of table, view, synonym, or sequence.
- `owner` (`CHAR(8)`): table owner (`system` by default).
- `dirpath` (`CHAR(64)`): name of the file that physically stores the data.
- `tabid` (`SERIAL`): sequential identification number of the table assigned by the system, from 150 onwards.
- `38s`: remaining unknown data pending analysis:
  - `rowsize`
  - `ncols`
  - `nindexes`
  - `nrows`
  - `created`
  - `version`
  - `tabtype`
  - `nfkeys`
  - `part1`
  - `part2`
  - `part3`
  - `part4`
  - `part5`
  - `part6`
  - `part7`
  - `part8`
- `\n`: end of record.

## `syscolumns.dat`
Currently, the string `">18sLHHH1s"` is used to obtain the information. The format string `">18sLHHH1s"` breaks down as follows:

- `colname` (`CHAR(18)`): column name.
- `tabid` (`SERIAL`): sequential identification number of the table assigned by the system.
- `colno` (`SMALLINT`): column number, starting from 1.
- `coltype` (`SMALLINT`): column type.
- `collength` (`SMALLINT`): column length.
- `\n`: end of record.

# Useful links

This project started with the idea that Multibase was out of support and it was not possible to find the necessary tools to perform data export. I have located the official website of the product where they even have an evaluation version. Below I share the most interesting links to complete this work:

* Homepage: https://multibase.tech/
* Link to the evaluation copy: https://multibase.tech/descargas/
* Multibase, programmer's manual: https://www.base100.com/es/productos/pdf/manuales/multibase/mbprogramador.pdf