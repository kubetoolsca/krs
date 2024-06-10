from difflib import SequenceMatcher
from math import e
import re, json
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder for complex objects not serializable by default json code.
    """
    def default(self, obj: object) -> object:
        
        """
        Serialize datetime objects to ISO 8601 format.
        
        Args:
            obj (object): Object to serialize.
            
        Returns:
            object: Serialized object.
        """
        try:
            if isinstance(obj, datetime):
                # Format datetime object as a string in ISO 8601 format
                return obj.isoformat()
            # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)
        except TypeError as e:
            return str(obj)
        except Exception as e:
            raise e
        except:
            print("An error occurred during serialization.")
            raise

def similarity(a : str, b: str) -> float:
    """
    Calculate the similarity ratio between two strings using SequenceMatcher.
    
    Args:
        a (str): First string.
        b (str): Second string.
    Returns:
        float: Similarity ratio between the two strings.
        
    """
    
    try:
        return SequenceMatcher(None, a, b).ratio()
    except Exception as e:
        print(f"An error occurred during similarity calculation: {e}")
        return 0.0
    except:
        print("An error occurred during similarity calculation.")
        return 0.0

def filter_similar_entries(log_entries : list) -> list:
    
    """
    Filter out highly similar log entries from a list of log entries.
    
    Args:
        log_entries (list): List of log entries.
    Returns:
        list: Filtered list of log entries.
    """
    
    try:
        unique_entries = list(log_entries)
        to_remove = set()

        # Compare each pair of log entries
        for i in range(len(unique_entries)):
            for j in range(i + 1, len(unique_entries)):
                if similarity(unique_entries[i], unique_entries[j]) > 0.85:
                    # Choose the shorter entry to remove, or either if they are the same length
                    if len(unique_entries[i]) > len(unique_entries[j]):
                        to_remove.add(unique_entries[i])
                    else:
                        to_remove.add(unique_entries[j])

        # Filter out the highly similar entries
        filtered_entries = {entry for entry in unique_entries if entry not in to_remove}
        return filtered_entries
    except Exception as e:
        print(f"An error occurred during filtering of log entries: {e}")
        return []
    except:
        print("An error occurred during filtering of log entries.")
        return []


def extract_log_entries(log_contents : str) -> list:
    
    """
    Extract log entries from a string containing log data.
    
    Args:
        log_contents (str): String containing log data.
    Returns:
        list: List of extracted log entries.
    """
    
    
    # Patterns to match different log formats
    
    try:
        patterns = [
            re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}Z\s+(warn|error)\s+\S+\s+(.*)', re.IGNORECASE),
            re.compile(r'[WE]\d{4} \d{2}:\d{2}:\d{2}.\d+\s+\d+\s+(.*)'),
            re.compile(r'({.*})')  
        ] # JSON log entry pattern

        log_entries = set()
        # Attempt to match each line with all patterns
        for line in log_contents.split('\n'):
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    if match.groups()[0].startswith('{'):
                        # Handle JSON formatted log entries
                        try:
                            log_json = json.loads(match.group(1)) # Extract JSON object
                            if 'severity' in log_json and log_json['severity'].lower() in ['error', 'warning']: # Check for severity
                                level = "Error" if log_json['severity'] == "ERROR" else "Warning" # Map severity to Error or Warning
                                message = log_json.get('error', '') if 'error' in log_json.keys() else line # Extract error message
                                log_entries.add(f"{level}: {message.strip()}") # Add formatted log entry
                            elif 'level' in log_json: # Check for level
                                level = "Error" if log_json['level'] == "error" else "Warning" # Map level to Error or Warning
                                message = log_json.get('msg', '')  + log_json.get('error', '') # Extract message
                                log_entries.add(f"{level}: {message.strip()}") # Add formatted log entry
                        except json.JSONDecodeError: # Skip if JSON is not valid
                            continue  # Skip if JSON is not valid
                    else:
                        if len(match.groups()) == 2:
                            level, message = match.groups()
                        elif len(match.groups()) == 1:
                            message = match.group(1)  # Assuming error as default
                            level = "ERROR"  # Default if not specified in the log

                        level = "Error" if "error" in level.lower() else "Warning" # Map level to Error or Warning
                        formatted_message = f"{level}: {message.strip()}" # Format log entry
                        log_entries.add(formatted_message) # Add formatted log entry
                    break  # Stop after the first match

        return filter_similar_entries(log_entries) # Filter out highly similar log entries

    except Exception as e:
        print(f"An error occurred during pattern creation: {e}")
        return []
    except:
        print("An error occurred during pattern creation.")
        return []