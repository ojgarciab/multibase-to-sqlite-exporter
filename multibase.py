import os
from typing import List
from struct import unpack

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

class ColType:
    CHAR = 0
    SMALLINT = 1
    INTEGER = 2
    TIME = 3
    DECIMAL = 5
    SERIAL = 6
    DATE = 7

    def get_size(column: Column):
        if column.coltype == ColType.CHAR:
            return column.collength
        elif column.coltype == ColType.SMALLINT:
            return 2
        elif column.coltype == ColType.INTEGER:
            return 4
        elif column.coltype == ColType.TIME:
            raise Exception("Not implemented")
        elif column.coltype == ColType.DECIMAL:
            raise Exception("Not implemented")
        elif column.coltype == ColType.SERIAL:
            return 4
        elif column.coltype == ColType.DATE:
            raise Exception("Not implemented")
        else:
            raise Exception("Unknown data type for the column")

    def get_format(column: Column):
        if column.coltype == ColType.CHAR:
            return f'{column.collength}s'
        elif column.coltype == ColType.SMALLINT:
            return f'h'
        elif column.coltype == ColType.INTEGER:
            return f'l'
        elif column.coltype == ColType.TIME:
            raise Exception("Not implemented")
        elif column.coltype == ColType.DECIMAL:
            raise Exception("Not implemented")
        elif column.coltype == ColType.SERIAL:
            return f'L'
        elif column.coltype == ColType.DATE:
            raise Exception("Not implemented")
        else:
            raise Exception("Unknown data type for the column")

class FileNames:
    FILE_EXTENSION = ".dat"
    SYSTABLES = "systables.dat"

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
        self.read_table(FileNames.SYSTABLES, [
            Column("tabname", 1, 1, ColType.CHAR, 18),
            Column("owner", 1, 2, ColType.CHAR, 8),
            Column("dirpath", 1, 3, ColType.CHAR, 64),
            Column("tabid", 1, 4, ColType.SERIAL, 4),
            Column("rest", 1, 5, ColType.CHAR, 37),
        ])

    def read_table(self, filename: str, columns: List[Column], ignore_file_extension=False):
        if not filename.endswith(FileNames.FILE_EXTENSION) and not ignore_file_extension:
            filename += FileNames.FILE_EXTENSION
        # contains the carriage return of each read record at the end
        row_size = 1
        format = ">"
        for column in columns:
            format += ColType.get_format(column)
            row_size += ColType.get_size(column)
        format += "1s"
        print(f'Format: "{format}", row_size: {row_size}{os.linesep}')
        with open(os.path.join(self.path, filename), 'rb', newline=None) as file:
            while (line := file.read(row_size)):
                if len(line) == row_size:
                    row = unpack(format, line)
                    print(row)
                    print(os.linesep)
                    #.decode(encoding='iso-8859-1').strip()