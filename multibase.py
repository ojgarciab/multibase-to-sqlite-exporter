"""Module that implements MySQL database reading."""

# pylint: disable=too-many-arguments,line-too-long

import os.path
from struct import unpack
from datetime import date, time, timedelta

base_date = date(1899, 12, 31)

class Decimal(float):
    """Class that stores a decimal value (serializable in JSON)"""
    number = ""
    def __new__(cls, binary_data: bytes, collength: int) -> float:
        cls.number = ""
        # We extract the necessary data from the header in order to reconstruct the decimal value
        decimal_places = collength & 255
        is_positive = binary_data[0] > 127
        decimal_position = (binary_data[0] & 0b00001111) * 2
        # We convert each byte into a numerical value with two digits
        for i in range(1, len(binary_data)):
            figures = binary_data[i]
            if not is_positive:
                figures = 100 - figures
            cls.number += str(figures)[-2:].zfill(2)
        # We add the decimal point at the specified position in the header
        cls.number = cls.number[:decimal_position] + "." + cls.number[decimal_position:decimal_position + decimal_places]
        if not is_positive:
            cls.number = "-" + cls.number
        return float.__new__(cls, cls.number)

class Date(str):
    """Class that stores a date value (serializable in JSON)"""
    date = None
    def __new__(cls, days: int):
        if days == 0x80000000:
            cls.date = None
            return None
        cls.date = base_date + timedelta(days=days if days < 47483 else 0)
        return str.__new__(cls, cls.date.isoformat())

class Time(str):
    """Class that stores a time value (serializable in JSON)"""
    time = None
    def __new__(cls, seconds: int):
        cls.time = time(seconds // 3600, (seconds % 3600) // 60, seconds % 60)
        return str.__new__(cls, cls.time.isoformat())

class Column(dict):
    """Class that stores the fields of a table (serializable in JSON)"""

    CHAR = 0
    SMALLINT = 1
    INTEGER = 2
    TIME = 3
    DECIMAL = 5
    SERIAL = 6
    DATE = 7

    colname: str
    tabid: int
    colno: int
    coltype: int
    collength: int

    def __init__(self, colname: str, tabid: int, colno: int, coltype: int, collength: int):
        dict.__init__(
            self,
            colname=colname,
            tabid=tabid,
            colno=colno,
            coltype=coltype,
            collength=collength
        )
        self.colname = colname
        self.tabid = tabid
        self.colno = colno
        self.coltype = coltype
        self.collength = collength

    def __str__(self) -> str:
        return f'Column("{repr(self.colname)}", {self.tabid}, {self.colno}, {self.coltype}, {self.collength})'

    def get_size(self):
        """Calculate the size that the record occupies in memory according to its type."""
        coltype = self.coltype & 0xff
        if coltype == self.DECIMAL:
            # The length in bytes is half of the sum of the number of integer and decimal digits, rounded up.
            length = (self.collength >> 8) + (self.collength % 256)
            return (length + 1) // 2
        #elif self.coltype > self.DATE:
        #    raise NotImplementedError(f"Coltype #{self.coltype} ({self.colname}) not implemented")
        return self.collength

    def get_format(self):
        """Get the most appropriate unpack format for the record type."""
        coltype = self.coltype & 0xff
        if coltype == self.SMALLINT:
            return 'h'
        if coltype == self.INTEGER:
            return 'l'
        if coltype == self.DECIMAL:
            length = (self.collength >> 8) + (self.collength % 256)
            return f"{str((length + 1) // 2)}s"
        if coltype in (
            self.TIME,
            self.SERIAL,
            self.DATE
        ):
            return 'L'
        #elif self.coltype > self.DATE:
        #    raise NotImplementedError(f"Coltype #{self.coltype} ({self.colname}) not implemented")
        return f'{self.collength}s'

class MultibaseReader:
    """A class for reading multibase databases."""

    FILE_EXTENSION = ".dat"
    SYSTABLES = "systables"
    SYSCOLUMNS = "syscolumns"

    # The path of the directory where the database is stored
    path = None
    # The tables and columns loaded in memory
    tables = None
    columns = None
    # Initial basic schema of the database
    schema = {
        "systables": {
            "filename": "systables.dat",
            "columns": [
                Column("tabname", 1, 1, Column.CHAR, 18),
                Column("owner", 1, 2, Column.CHAR, 8),
                Column("dirpath", 1, 3, Column.CHAR, 64),
                Column("tabid", 1, 4, Column.SERIAL, 4),
                Column("rest", 1, 5, Column.CHAR, 37),
            ],
        },
        "syscolumns": {
            "filename": "syscolumns.dat",
            "columns": [
                Column("colname", 1, 1, Column.CHAR, 18),
                Column("tabid", 1, 2, Column.SERIAL, 4),
                Column("colno", 1, 3, Column.SMALLINT, 2),
                Column("coltype", 1, 4, Column.SMALLINT, 2),
                Column("collength", 1, 5, Column.SMALLINT, 2),
            ],
        },
    }

    def __init__(self, path, preload=True):
        """
        Constructor for MultiBaseReader.

        Parameters:
        path (str): The path of the directory where the database is stored.
        preload_tables (bool): Whether to preload the tables or not.
        """
        # Raise an exception if the provided path is not a directory
        if not os.path.isdir(path):
            raise FileNotFoundError("The provided path is not a directory")
        self.path = os.path.abspath(path)
        if preload:
            self.build_schema()

    def build_schema(self):
        """Buils schema from basic structure of files"""
        tables = self.read_table(self.SYSTABLES)
        tables_dict = {}
        for table in tables:
            tabname = table["tabname"]
            tables_dict[tabname] = {k: v for k, v in table.items() if k != "tabname"}
        del tables
        columns = self.read_table(self.SYSCOLUMNS)
        columns_dict = {}
        for column in columns:
            tabid = column["tabid"]
            if tabid not in columns_dict:
                columns_dict[tabid] = []
            columns_dict[tabid].append(column)
        del columns
        # We reconstruct the database schema
        self.schema = {}
        for table_name, table_data in tables_dict.items():
            columns = []
            if table_data["tabid"] not in columns_dict:
                continue
            for column in columns_dict[table_data["tabid"]]:
                columns.append(
                    Column(
                        column["colname"],
                        column["tabid"],
                        column["colno"],
                        column["coltype"],
                        column["collength"]
                    )
                )
            self.schema[table_name] = {
                "filename": table_data["dirpath"] + self.FILE_EXTENSION,
                "columns": columns,
            }

    def read_table(
        self,
        tablename: str,
        trim=True
    ):
        """
        Reads all records from a table on disk.

        Parameters:
        tablename (str): The table name.
        trim (bool): Whether to trim CHAR values or not.
        """
        if not tablename in self.schema:
            raise LookupError("The table does not exist or 'build_schema()' has not been called.")
        columns = self.schema[tablename]["columns"]
        # It includes the carriage return at the end of each record
        row_size = 1
        # The data is stored in big-endian format
        format_string = { 0: ">" }
        for column in columns:
            format_string[column.colno] = column.get_format()
            row_size += column.get_size()
        format_string = "".join(format_string[key] for key in sorted(format_string.keys())) + "1s"
        result = []
        with open(os.path.join(self.path, self.schema[tablename]["filename"]), 'rb', newline=None) as file:
            while (line := file.read(row_size)):
                # Check if the record has been deleted (overwritten with null values)
                # and we have read a complete record
                if all(byte == 0 for byte in line) or len(line) != row_size:
                    continue
                row = {}
                data = unpack(format_string, line)
                for column in columns:
                    coltype =column.coltype & 0xff
                    if coltype == Column.CHAR:
                        # Decode the character string from the database character set, iso-8859-1
                        row[column.colname] = data[column.colno - 1].decode(
                            encoding='iso-8859-1'
                            ).strip()
                    elif coltype == Column.DECIMAL:
                        row[column.colname] = Decimal(data[column.colno - 1], column.collength)
                    elif coltype == Column.DATE:
                        row[column.colname] = Date(data[column.colno - 1])
                    elif coltype == Column.TIME:
                        row[column.colname] = Time(data[column.colno - 1])
                    elif coltype in (
                        Column.INTEGER,
                        Column.SMALLINT,
                        Column.SERIAL
                    ):
                        row[column.colname] = data[column.colno - 1]
                    else:
                        # Decode the character string from the database character set, iso-8859-1
                        row[column.colname] = data[column.colno - 1].decode(
                            encoding='iso-8859-1'
                        )
                        if trim:
                            row[column.colname] = row[column.colname].strip()
                result.append(row)
        return result
