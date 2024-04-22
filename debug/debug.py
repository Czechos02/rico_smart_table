from enum import Enum


class DBGLevel(Enum):
    NONE = 0
    CRITICAL = 1
    ERROR = 3
    WARN = 4
    INFO = 5
    DETAILS = 6


global_dbg_level = DBGLevel.CRITICAL


def debug(dbg_level=DBGLevel.ERROR, message="Unknown error"):
    if dbg_level.value <= global_dbg_level.value:
        print(str(dbg_level) + "\t" + message)
