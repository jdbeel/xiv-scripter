from enum import IntEnum
from typing import Union

class LogLevel(IntEnum):
    QUIET = 0
    INFO = 1
    DEBUG = 2 

def dprint(verbose: Union[int, bool], string: str, default_priority: int = LogLevel.INFO):
    """
    Print a message to stdout if `verbose` >= default_priority.

    Parameters
    ----------
    verbose: int or bool
        The verbosity of the string to print. Can be any of the
        values found in `utilities.LogLevel`. If bool, will be
        converted to an int.

    string: str
        The string to print.

    default_priority: int, default LogLevel.INFO
        (Optional) the priority of the message. If `verbose` exceeds this value,
        the message will be printed. Otherwise, nothing will be printed.
    """
    if isinstance(verbose, bool):
        verbose = int(verbose)

    if verbose >= default_priority:
        print(string)