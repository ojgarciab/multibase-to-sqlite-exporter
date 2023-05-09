import os
from typing import List
from enum import Enum
from struct import unpack

class ColType(Enum):
    CHAR = 0
    SMALLINT = 1
    INTEGER = 2
    TIME = 3
    DECIMAL = 5
    SERIAL = 6
    DATE = 7

class FileNames(Enum):
    FILE_EXTENSION = ".dat"
    SYSTABLES = "systables.dat"

class Column:
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

class MultibaseReader:
    """
    A class for reading multibase databases.
    """

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
        self.read_table(FileNames.SYSTABLES.value, [
            Column("tabname", 1, 1, ColType.CHAR, 18),
            Column("owner", 1, 2, ColType.CHAR, 8),
            Column("dirpath", 1, 3, ColType.CHAR, 64),
            Column("tabid", 1, 4, ColType.SERIAL, 4),
            Column("rest", 1, 5, ColType.CHAR, 39),
        ])

    def read_table(self, filename: str, columns: List[Column]):
        if not filename.endswith(FileNames.FILE_EXTENSION.value):
            filename += FileNames.FILE_EXTENSION.value
        # contains the carriage return of each read record at the end
        row_size = 1
        format = ">"
        for column in columns:
            if column.coltype == ColType.CHAR:
                row_size += column.collength
                format += f'{column.collength}s'
            elif column.coltype == ColType.SMALLINT:
                row_size += 2
                format += f'h'
            elif column.coltype == ColType.INTEGER:
                row_size += 2
                format += f'h'
            elif column.coltype == ColType.TIME:
                raise Exception("Not implemented")
            elif column.coltype == ColType.DECIMAL:
                raise Exception("Not implemented")
            elif column.coltype == ColType.SERIAL:
                row_size += 2
                format += f'h'
            elif column.coltype == ColType.DATE:
                raise Exception("Not implemented")
            else:
                raise Exception("Unknown data type for the column")
        format += "1s"
        print(f'Format: "{format}", row_size: {row_size}{os.linesep}')
        with open(os.path.join(self.path, filename), 'rb', newline=None) as file:
            while (line := file.read(row_size)):
                if len(line) == row_size:
                    print(unpack(format, line))
                    print(os.linesep)
