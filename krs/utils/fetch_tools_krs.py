import json
import requests
import yaml
from krs.utils.constants import (KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH, CNCF_YMLPATH, CNCF_YMLURL, CNCF_TOOLS_JSONPATH, TOOLS_RANK_JSONPATH, CATEGORY_RANK_JSONPATH)



# Function to convert 'githubStars' to a float, or return 0 if it cannot be converted
def get_github_stars(tool: dict) -> float:
    
    """
    get_github_stars checks for the tool’s star rating, if one exists, 
    it returns the star rating as a float data type, else, it returns 0.

    Args:
    -tool(dict) - Arg that holds info about a tool.

    Returns:
    -float: A tool’s star rating

    """
    try:
        stars = tool.get('githubStars', 0)
        return float(stars)
    except ValueError as e:
        print(f"Error: {e}")
        return {}
    except TypeError as e:
        print(f"Error: {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}
    except:
        print("An error occurred while converting the star rating.")
        return {}
    
    
# Function to download and save a file
def download_file(url: str, filename: str) -> None:
    
    """
    Downloads a file from the specified URL and saves it to the given filename.

    Args:
        url (str): The URL of the file to download.
        filename (str): The path to save the downloaded file.

    Returns:
        None
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        with open(filename, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {}
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}
    except:
        print("An error occurred while downloading the file.")
        return {}

def parse_yaml_to_dict(yaml_file_path: str) -> dict:
    
    """
    Parses a YAML file and returns a dictionary with tool names as keys and their statuses as values.

    This function specifically targets the structure of the CNCF landscape YAML file, extracting tool names and their project statuses.

    Args:
        yaml_file_path (str): The file path of the YAML file to parse.

    Returns:
        dict: A dictionary with tool names as keys and their project statuses as values.
    """
    
    try:
        with open(yaml_file_path, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file {yaml_file_path} was not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing the YAML file: {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}
    except:    
        print("An error occurred while parsing the YAML file.")
        return {}
    
    cncftools = {}
    
    try:
        
        # Extract tool names and project statuses from the CNCF landscape YAML file
        for category in data.get('landscape', []):
            for subcategory in category.get('subcategories', []):
                for item in subcategory.get('items', []):
                    item_name = item.get('name').lower()
                    project_status = item.get('project', 'listed')
                    cncftools[item_name] = project_status
    except AttributeError as e:
        print(f"Error processing the YAML file: {e}")
        return {}
    except ValueError as e:
        print(f"Error processing data: {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}
    except:
        print("An error occurred while processing the YAML file.")
        return {}
    
    return {'cncftools': cncftools}

def save_json_file(jsondict: dict, jsonpath: str) -> None:

    """
    Saves a dictionary to a JSON file at the specified path.

    This function takes a dictionary and writes it to a JSON file, formatting the output for readability.

    Args:
        jsondict (dict): The dictionary to save.
        jsonpath (str): The file path where the JSON file will be saved.

    Returns:
        None
    """

    try:
        # Write the category dictionary to a new JSON file
        with open(jsonpath, 'w') as f:
            json.dump(jsondict, f, indent=4)
    except FileNotFoundError as e:  
        print(f"Error: {e}")
        return {}
    except Exception as e:        
        print(f"Error: {e}")
        return {}
    except:
        print("An error occurred while saving the JSON file.")
        return {}


def krs_tool_ranking_info()-> tuple:
    
    """
    krs_tool_ranking_info fetches the tool ranking data from the KubeTools API and the CNCF landscape YAML file,
    processes this data to rank tools within categories based on GitHub stars, and saves the processed data to JSON files.

    Returns:
        Tuple containing three dictionaries:
        - tools_dict: Dictionary mapping tool names to their rankings, categories, and URLs.
        - category_tools_dict: Dictionary mapping category names to dictionaries of tools ranked within the category.
        - cncf_tools_dict: Dictionary representing the parsed CNCF landscape YAML file.
    """
    
    
    # New dictionaries 
    tools_dict = {}
    category_tools_dict = {}

    try:
        download_file(KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH) # Download the KubeTools JSON file
        download_file(CNCF_YMLURL, CNCF_YMLPATH) # Download the CNCF landscape YAML file
    except Exception as e:
        print(f"Error: {e}")
        return {}
    except:
        print("An error occurred while downloading the files.")
        return {}
    
    try:
        with open(KUBETOOLS_JSONPATH) as f:
            data = json.load(f)
    
        # Process the KubeTools data to rank tools within categories based on GitHub stars
        for category in data:
            # Sort the tools in the current category by the number of GitHub stars
            sorted_tools = sorted(category['tools'], key=get_github_stars, reverse=True)

            for i, tool in enumerate(sorted_tools, start=1):
                tool["name"] = tool['name'].replace("\t", "").lower()
                tool['ranking'] = i

                # Update tools_dict
                tools_dict.setdefault(tool['name'], []).append({
                    'rank': i,
                    'category': category['category']['name'],
                    'url': tool['link']
                })

                # Update category_tools_dict
                category_tools_dict.setdefault(category['category']['name'], {}).update({i: {'name': tool['name'], 'url': tool['link']}})
        

        cncf_tools_dict = parse_yaml_to_dict(CNCF_YMLPATH) # Parse the CNCF landscape YAML file
        save_json_file(cncf_tools_dict, CNCF_TOOLS_JSONPATH) # Save the CNCF landscape dictionary to a JSON file
        save_json_file(tools_dict, TOOLS_RANK_JSONPATH) # Save the tools dictionary to a JSON file
        save_json_file(category_tools_dict, CATEGORY_RANK_JSONPATH) # Save the category dictionary to a JSON file

        return tools_dict, category_tools_dict, cncf_tools_dict

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}
    except:   
        print("An error occurred while processing the data.")
        return {}

if __name__=='__main__':
    tools_dict, category_tools_dict, cncf_tools_dict = krs_tool_ranking_info()
    print(cncf_tools_dict)

