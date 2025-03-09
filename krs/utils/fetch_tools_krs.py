import json
import requests
import yaml
from krs.utils.constants import (KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH, CNCF_YMLPATH, CNCF_YMLURL, CNCF_TOOLS_JSONPATH, TOOLS_RANK_JSONPATH, CATEGORY_RANK_JSONPATH)

# Function to convert 'githubStars' to a float, or return 0 if it cannot be converted
def get_github_stars(tool):
    stars = tool.get('rankedScore', 0)
    try:
        return float(stars)
    except ValueError:
        return 0.0
    
# Function to download and save a file
def download_file(url, filename):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    with open(filename, 'wb') as file:
        file.write(response.content)

def parse_yaml_to_dict(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    
    cncftools = {}
    
    for category in data.get('landscape', []):
        for subcategory in category.get('subcategories', []):
            for item in subcategory.get('items', []):
                item_name = item.get('name').lower()
                project_status = item.get('project', 'listed')
                cncftools[item_name] = project_status
    
    return {'cncftools': cncftools}

def save_json_file(jsondict, jsonpath):

    # Write the category dictionary to a new JSON file
    with open(jsonpath, 'w') as f:
        json.dump(jsondict, f, indent=4)


def krs_tool_ranking_info():
    # New dictionaries 
    tools_dict = {}
    category_tools_dict = {}

    download_file(KUBETOOLS_DATA_JSONURL, KUBETOOLS_JSONPATH)
    download_file(CNCF_YMLURL, CNCF_YMLPATH)

    with open(KUBETOOLS_JSONPATH, encoding='utf-8') as f:
        data = json.load(f)

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

            # Update ranked_tools_dict
            category_tools_dict.setdefault(category['category']['name'], {}).update({i: {'name': tool['name'], 'url': tool['link']}})
    

    cncf_tools_dict = parse_yaml_to_dict(CNCF_YMLPATH)
    save_json_file(cncf_tools_dict, CNCF_TOOLS_JSONPATH)
    save_json_file(tools_dict, TOOLS_RANK_JSONPATH)
    save_json_file(category_tools_dict, CATEGORY_RANK_JSONPATH)

    return tools_dict, category_tools_dict, cncf_tools_dict

if __name__=='__main__':
    tools_dict, category_tools_dict, cncf_tools_dict = krs_tool_ranking_info()
    print(cncf_tools_dict)

