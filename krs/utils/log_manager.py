import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime, timedelta
from pathlib import Path


class RotatingFileHandlerWithLevel(TimedRotatingFileHandler):
    """
    Custom TimedRotatingFileHandler with configurable log level and deletion.
    """

    def __init__(self, filename : str, when: str = 'midnight', interval: int = 1, backupCount: int =7, level: any =logging.DEBUG, formatter: any =None, **kwargs: any) -> None:
        """
        Initialize the handler.
        
        args:
            filename: str: The filename of the log file.
            when: str: The type of interval. Default is 'midnight'.
            interval: int: The interval of rotation. Default is 1.
            backupCount: int: The number of backup files to keep. Default is 7.
            level: int: The log level. Default is logging.DEBUG.
            formatter: logging.Formatter: The formatter to use. Default is None.
            **kwargs: Any additional keyword arguments.
        
        returns:
            None
        """
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, **kwargs)
        self.setLevel(level)
        if formatter:
            self.setFormatter(formatter)

    def emit(self, record: any)-> None:
        """
        Emit a log record.
        
        args:
            record: logging.LogRecord: The log record to emit.
            
        returns:
            None"""
        if record.levelno >= self.level:
            super().emit(record)

def handle_old_file():
    """
    Handle old log files.

    args:
        None
    returns:
        None
    """

    seven_days_ago = datetime.now() - timedelta(days=7)

    # Get the absolute path to the target folder
    script_dir = Path(__file__).parent.absolute()
    target_folder = script_dir / "logs"

    try:
        target_folder.mkdir(parents=True, exist_ok=True)
        filename = f"{target_folder}/{seven_days_ago.date()}.log"
        remove_a_file(filename)
    except PermissionError as e:
        print(f"Permission denied: You do not have the necessary permissions to create the directory {target_folder}: {e}.")
        return None
    except FileNotFoundError as e:
        print(f"FileNotFoundError: The system cannot find the path specified: {target_folder}: {e}.")
        return None
    except Exception as e:
        print(f"An error occurred while creating the directory {target_folder}: {e}")
        return None
    except:
        print(f"An error occurred while creating the directory {target_folder}.")
        return None


def remove_a_file(filename: str) -> None:
    """
    Remove log files older than a week.
    
    args:
        filename: str: The file containing the logs .
    
    returns:
        None
    """
    
    try:

        if os.path.isfile(filename):
            os.remove(filename)
            print(f"{filename} has been deleted.")
        else:
            print(f"The file {filename} does not exist.")

    except PermissionError as e:
        print(f"Permission denied: You do not have the necessary permissions to delete {filename}: {e}.")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: The system cannot find the file specified: {filename}: {e}.")
    except Exception as e:
        print(f"An error occurred while deleting {filename}: {e}")
    except:
        print(f"An error occurred while deleting the file {filename}.")


def krs_logger(log_level: any=logging.ERROR, target_folder: str ="logs") -> tuple:
    """
    Creates a logger with RotatingFileHandler and configurable log level.
    
    args:
        log_level: int: The log level. Default is logging.ERROR.
        target_folder: str: The folder to store the log files. Default is 'logs'.
    returns:
        logger: logging.Logger: The logger object.
        log_with_exc_info: function: The function to log with exception info.
    
    """
    # Get the absolute path to the target folder
    script_dir = Path(__file__).parent.absolute()
    target_folder = script_dir / target_folder

    handle_old_file()

    try:
        target_folder.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Permission denied: You do not have the necessary permissions to create the directory {target_folder}.")
        return None, None
    except FileNotFoundError:
        print(f"FileNotFoundError: The system cannot find the path specified: {target_folder}")
        return None, None
    except Exception as e:
        print(f"An error occurred while creating the directory {target_folder}: {e}")
        return None, None
    except:
        print(f"An error occurred while creating the directory {target_folder}.")
        return None, None
    
    try:
        
        handler = RotatingFileHandlerWithLevel(
            f"{target_folder}/{datetime.now().strftime('%Y-%m-%d')}.log",
            when="midnight",
            interval=1,  # Change to 1 for daily rotation
            backupCount=7,
            level=log_level,
            formatter=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"),
        )
    except PermissionError as e:
        print(f"Permission denied: You do not have the necessary permissions to create the log file: {e}")
        return None, None
    except FileNotFoundError as e:
        print(f"FileNotFoundError: The system cannot find the path specified: {e}")
        return None, None
    except Exception as e:
        print(f"An error occurred while creating the log file: {e}")
        return None, None
    except:
        print("An error occurred while creating the log file.")
        return None, None

    logger = logging.getLogger("krs") # Get/Create the logger
    logger.setLevel(log_level) # Set the log level
    logger.addHandler(handler) # Add the handler to the logger

    def log_with_exc_info(message: str, exc_info: bool = False, *args: any, **kwargs: any) -> None:
        
        """
        Log a message with exception info.
        
        args:
            message: str: The message to log.
            exc_info: bool: Whether to log the exception info. Default is False.
            *args: any: Additional positional arguments.
            **kwargs: any: Additional keyword arguments.
        
        returns:
            None
        """
        
        if exc_info and kwargs.get("exc_info") is True:
            # Extract exception and traceback from kwargs
            exc_type, exc_value, traceback = kwargs["exc_info"]
            # Log the formatted traceback
            logger.exception(f"{message}\nTraceback:\n{traceback}")
        else:
            logger.log(log_level, message, *args, **kwargs)

    return logger, log_with_exc_info

