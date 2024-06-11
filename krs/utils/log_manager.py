from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
from datetime import datetime
from krs.utils.constants import LOG_HISTORY_PATH


def write_to_log_file(log_info: list) -> None:
    
    """
    Write log information to a file.
    
    Args:
        log_info (list): List of log information to write to the file.
    Returns:
        None
    """
    
    try:
        directory = os.path.dirname(LOG_HISTORY_PATH)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(LOG_HISTORY_PATH + 'log_' + (datetime.now().date()).strftime("%d-%m-%Y") + '.txt', 'a') as file:
            for log in log_info:
                file.write(f"{datetime.now()} - {log}\n")
    except Exception as e:
        print(f"An error occurred while writing to the log file: {e}")
    except:
        print("An error occurred while writing to the log file.")
    
    
def schedule_log_update(log_info: list) -> None:
    
    """
    Schedule the log update job to run every day at specific times.
    
    Args:
        log_info (list): List of log information to write to the file.
    Returns:
        None
    """
    try:
        
        scheduler = BackgroundScheduler()

        # Schedule the job to run every day at specific times
        scheduler.add_job(write_to_log_file, 'cron', hour=00, minute=01, args=[log_info])  # Runs at 2:30 PM every day
        

        # Start the scheduler
        scheduler.start()

        try:
            # Keep the script running to let the scheduler do its job
            while True:
                time.sleep(1) # Sleep for 1 second
        except (KeyboardInterrupt, SystemExit):
            # Shut down the scheduler on exit
            scheduler.shutdown()
            
    except Exception as e:
        print(f"An error occurred while scheduling the log update job: {e}")
    except:
        print("An error occurred while scheduling the log update job.")
        
def log_handler(log_info: list) -> None:
    
    """
    
    Handle the log information and write it to a file.
    
    Args:
        log_info (list): List of log information to write to the file.
    Returns:
        None
    """
    
    try:
    
        current_date = datetime.now().date()

        # Get date of 7 days ago
        date_seven_days_ago = current_date - timedelta(days=7)

        file_path = LOG_HISTORY_PATH + 'log_' + date_seven_days_ago.strftime("%d-%m-%Y") + '.txt'

        if(os.path.exists(file_path)):
            os.remove(file_path)

        schedule_log_update(log_info)
        
    except Exception as e:
        print(f"An error occurred while handling the log information: {e}")
    except:
        print("An error occurred while handling the log information.")