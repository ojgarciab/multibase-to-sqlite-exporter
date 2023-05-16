"""Module that implements MySQL database reading."""

# pylint: disable=too-many-arguments

import os.path
from typing import List
from struct import unpack

class Column:
    """Class that stores the fields of a table"""

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
        self.colname = colname
        self.tabid = tabid
        self.colno = colno
        self.coltype = coltype
        self.collength = collength

    def get_size(self):
        if self.coltype == self.CHAR:
            return self.collength
        if self.coltype == self.SMALLINT:
            return 2
        if self.coltype == self.INTEGER:
            return 4
        if self.coltype == self.TIME:
            raise NotImplementedError("Not implemented")
        if self.coltype == self.DECIMAL:
            raise NotImplementedError("Not implemented")
        if self.coltype == self.SERIAL:
            return 4
        if self.coltype == self.DATE:
            raise NotImplementedError("Not implemented")
        raise Exception("Unknown data type for the column")

    def get_format(self):
        if self.coltype == self.CHAR:
            return f'{self.collength}s'
        if self.coltype == self.SMALLINT:
            return 'h'
        if self.coltype == self.INTEGER:
            return 'l'
        if self.coltype == self.TIME:
            raise NotImplementedError("Not implemented")
        if self.coltype == self.DECIMAL:
            raise NotImplementedError("Not implemented")
        if self.coltype == self.SERIAL:
            return 'L'
        if self.coltype == self.DATE:
            raise NotImplementedError("Not implemented")
        raise Exception("Unknown data type for the column")

class MultibaseReader:
    """
    A class for reading multibase databases.
    """

    FILE_EXTENSION = ".dat"
    SYSTABLES = "systables.dat"

    # The path of the directory where the database is stored
    path = None
    # The tables loaded in memory
    tables = None

    def __init__(self, path, preload_tables=True):
        """
        Constructor for MultiBaseReader.

        Parameters:
        path (str): The path of the directory where the database is stored.
        preload_tables (bool): Whether to preload the tables or not.
        """
        # Raise an exception if the provided path is not a directory
        if not os.path.isdir(path):
            raise Exception("The provided path is not a directory")
        self.path = os.path.abspath(path)
        if preload_tables:
            self.tables = self.get_tables()

    def get_tables(self, refresh=False):
        if self.tables is not None and refresh:
            return self.tables
        self.read_table(self.SYSTABLES, [
            Column("tabname", 1, 1, Column.CHAR, 18),
            Column("owner", 1, 2, Column.CHAR, 8),
            Column("dirpath", 1, 3, Column.CHAR, 64),
            Column("tabid", 1, 4, Column.SERIAL, 4),
            Column("rest", 1, 5, Column.CHAR, 37),
        ])

    def read_table(
        self,
        filename: str,
        columns: List[Column],
        ignore_file_extension=False,
        trim=True
    ):
        if not filename.endswith(self.FILE_EXTENSION) and not ignore_file_extension:
            filename += self.FILE_EXTENSION
        # contains the carriage return of each read record at the end
        row_size = 1
        format = { 0: ">" }
        for column in columns:
            format[column.colno] = column.get_format()
            row_size += column.get_size()
        format = "".join(format[key] for key in sorted(format.keys())) + "1s"
        print(f'Format: "{format}", row_size: {row_size}{os.linesep}')
        result = []
        with open(os.path.join(self.path, filename), 'rb', newline=None) as file:
            while (line := file.read(row_size)):
                # Check if the record has been deleted (overwritten with null values)
                if all(byte == 0 for byte in line):
                    continue
                # Check if we have read a complete record
                if len(line) == row_size:
                    row = {}
                    data = unpack(format, line)
                    for column in columns:
                        if column.coltype == Column.CHAR and trim:
                            row[column.colname] = data[column.colno].decode(encoding='iso-8859-1').strip()
                        else:
                            row[column.colname] = data[column.colno]
                    print(row)
                    print(os.linesep)
                    #.decode(encoding='iso-8859-1').strip()
