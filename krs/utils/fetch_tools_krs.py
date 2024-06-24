# import json
# import requests
# import yaml
# from krs.utils.constants import (KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH, CNCF_YMLPATH, CNCF_YMLURL, CNCF_TOOLS_JSONPATH, TOOLS_RANK_JSONPATH, CATEGORY_RANK_JSONPATH)

# # Function to convert 'githubStars' to a float, or return 0 if it cannot be converted
# def get_github_stars(tool):
#     stars = tool.get('githubStars', 0)
#     try:
#         return float(stars)
#     except ValueError:
#         return 0.0
    
# # Function to download and save a file
# def download_file(url, filename):
#     response = requests.get(url)
#     response.raise_for_status()  # Ensure we notice bad responses
#     with open(filename, 'wb') as file:
#         file.write(response.content)

# def parse_yaml_to_dict(yaml_file_path):
#     with open(yaml_file_path, 'r') as file:
#         data = yaml.safe_load(file)
    
#     cncftools = {}
    
#     for category in data.get('landscape', []):
#         for subcategory in category.get('subcategories', []):
#             for item in subcategory.get('items', []):
#                 item_name = item.get('name').lower()
#                 project_status = item.get('project', 'listed')
#                 cncftools[item_name] = project_status
    
#     return {'cncftools': cncftools}

# def save_json_file(jsondict, jsonpath):

#     # Write the category dictionary to a new JSON file
#     with open(jsonpath, 'w') as f:
#         json.dump(jsondict, f, indent=4)


# def krs_tool_ranking_info():
#     # New dictionaries 
#     tools_dict = {}
#     category_tools_dict = {}

#     download_file(KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH)
#     download_file(CNCF_YMLURL, CNCF_YMLPATH)

#     with open(KUBETOOLS_JSONPATH) as f:
#         data = json.load(f)

#     for category in data:
#         # Sort the tools in the current category by the number of GitHub stars
#         sorted_tools = sorted(category['tools'], key=get_github_stars, reverse=True)

#         for i, tool in enumerate(sorted_tools, start=1):
#             tool["name"] = tool['name'].replace("\t", "").lower()
#             tool['ranking'] = i

#             # Update tools_dict
#             tools_dict.setdefault(tool['name'], []).append({
#                 'rank': i,
#                 'category': category['category']['name'],
#                 'url': tool['link']
#             })

#             # Update ranked_tools_dict
#             category_tools_dict.setdefault(category['category']['name'], {}).update({i: {'name': tool['name'], 'url': tool['link']}})
    

#     cncf_tools_dict = parse_yaml_to_dict(CNCF_YMLPATH)
#     save_json_file(cncf_tools_dict, CNCF_TOOLS_JSONPATH)
#     save_json_file(tools_dict, TOOLS_RANK_JSONPATH)
#     save_json_file(category_tools_dict, CATEGORY_RANK_JSONPATH)

#     return tools_dict, category_tools_dict, cncf_tools_dict

# if __name__=='__main__':
#     tools_dict, category_tools_dict, cncf_tools_dict = krs_tool_ranking_info()
#     print(cncf_tools_dict)



import json
import requests
import yaml
import logging
from krs.utils.constants import (
    KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH, CNCF_YMLPATH, CNCF_YMLURL,
    CNCF_TOOLS_JSONPATH, TOOLS_RANK_JSONPATH, CATEGORY_RANK_JSONPATH
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_github_stars(tool):
    """
    Converts 'githubStars' to a float, or returns 0 if it cannot be converted.
    
    Args:
        tool (dict): Dictionary containing tool information.

    Returns:
        float: Number of GitHub stars.
    """
    stars = tool.get('githubStars', 0)
    try:
        return float(stars)
    except ValueError:
        logging.warning("Unable to convert GitHub stars to float for tool: %s", tool.get('name'))
        return 0.0

def download_file(url, filename):
    """
    Downloads a file from a URL and saves it locally.
    
    Args:
        url (str): URL to download the file from.
        filename (str): Local filename to save the downloaded file.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        with open(filename, 'wb') as file:
            file.write(response.content)
        logging.info("Downloaded file from %s to %s", url, filename)
    except requests.RequestException as e:
        logging.error("Failed to download file from %s: %s", url, e)
        raise

def parse_yaml_to_dict(yaml_file_path):
    """
    Parses a YAML file and converts it to a dictionary.
    
    Args:
        yaml_file_path (str): Path to the YAML file.

    Returns:
        dict: Dictionary representation of the YAML file.
    """
    try:
        with open(yaml_file_path, 'r') as file:
            data = yaml.safe_load(file)
        cncftools = {}
        for category in data.get('landscape', []):
            for subcategory in category.get('subcategories', []):
                for item in subcategory.get('items', []):
                    item_name = item.get('name').lower()
                    project_status = item.get('project', 'listed')
                    cncftools[item_name] = project_status
        logging.info("Parsed YAML file %s successfully", yaml_file_path)
        return {'cncftools': cncftools}
    except Exception as e:
        logging.error("Failed to parse YAML file %s: %s", yaml_file_path, e)
        raise

def save_json_file(jsondict, jsonpath):
    """
    Saves a dictionary to a JSON file.
    
    Args:
        jsondict (dict): Dictionary to save.
        jsonpath (str): Path to the JSON file.
    """
    try:
        with open(jsonpath, 'w') as f:
            json.dump(jsondict, f, indent=4)
        logging.info("Saved JSON file to %s", jsonpath)
    except IOError as e:
        logging.error("Failed to save JSON file to %s: %s", jsonpath, e)
        raise

def sort_tools_by_stars(tools):
    """
    Sorts a list of tools by the number of GitHub stars in descending order.

    Args:
        tools (list): List of tool dictionaries.

    Returns:
        list: Sorted list of tool dictionaries.
    """
    return sorted(tools, key=get_github_stars, reverse=True)

def process_category_tools(data):
    """
    Processes tools in categories, ranks them, and updates dictionaries.

    Args:
        data (list): List of category data from the JSON file.

    Returns:
        tuple: Two dictionaries, one for tools and one for categories with rankings.
    """
    tools_dict = {}
    category_tools_dict = {}

    for category in data:
        sorted_tools = sort_tools_by_stars(category['tools'])
        for i, tool in enumerate(sorted_tools, start=1):
            tool["name"] = tool['name'].replace("\t", "").lower()
            tool['ranking'] = i
            tools_dict.setdefault(tool['name'], []).append({
                'rank': i,
                'category': category['category']['name'],
                'url': tool['link']
            })
            category_tools_dict.setdefault(category['category']['name'], {}).update({i: {'name': tool['name'], 'url': tool['link']}})
    return tools_dict, category_tools_dict

def krs_tool_ranking_info():
    """
    Main function to fetch, process, and save Kubernetes tool ranking information.

    Returns:
        tuple: Three dictionaries containing tools information, category tools information, and CNCF tools information.
    """
    download_file(KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH)
    download_file(CNCF_YMLURL, CNCF_YMLPATH)

    with open(KUBETOOLS_JSONPATH) as f:
        data = json.load(f)

    tools_dict, category_tools_dict = process_category_tools(data)
    cncf_tools_dict = parse_yaml_to_dict(CNCF_YMLPATH)

    save_json_file(cncf_tools_dict, CNCF_TOOLS_JSONPATH)
    save_json_file(tools_dict, TOOLS_RANK_JSONPATH)
    save_json_file(category_tools_dict, CATEGORY_RANK_JSONPATH)

    return tools_dict, category_tools_dict, cncf_tools_dict

if __name__=='__main__':
    tools_dict, category_tools_dict, cncf_tools_dict = krs_tool_ranking_info()
    print(cncf_tools_dict)
