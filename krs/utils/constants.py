# File paths for local data storage
KUBETOOLS_JSONPATH = 'krs/data/kubetools_data.json'
CNCF_YMLPATH = 'krs/data/landscape.yml'
CNCF_TOOLS_JSONPATH = 'krs/data/cncf_tools.json'
TOOLS_RANK_JSONPATH = 'krs/data/tools_rank.json'
CATEGORY_RANK_JSONPATH = 'krs/data/category_rank.json'
LLMSTATE_PICKLE_FILEPATH = 'krs/data/llmstate.pkl'
KRSSTATE_PICKLE_FILEPATH = 'krs/data/krsstate.pkl'
POD_INFO_FILEPATH = './exported_pod_info.json'

# URLs for fetching remote data
KUBETOOLS_DATA_JSONURL = 'https://raw.githubusercontent.com/Kubetools-Technologies-Inc/kubetools_data/main/data/kubetools_data.json'
CNCF_YMLURL = 'https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml'

# Directory paths
KRS_DATA_DIRECTORY = 'krs/data'

# Maximum number of output tokens for language model responses
MAX_OUTPUT_TOKENS = 512

def validate_file_paths():
    """
    Validates if the essential directories exist, and if not, creates them.
    This helps in avoiding errors during file operations.
    """
    import os

    directories = [
        os.path.dirname(KUBETOOLS_JSONPATH),
        os.path.dirname(CNCF_YMLPATH),
        os.path.dirname(CNCF_TOOLS_JSONPATH),
        os.path.dirname(TOOLS_RANK_JSONPATH),
        os.path.dirname(CATEGORY_RANK_JSONPATH),
        os.path.dirname(LLMSTATE_PICKLE_FILEPATH),
        os.path.dirname(KRSSTATE_PICKLE_FILEPATH),
        KRS_DATA_DIRECTORY
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created missing directory: {directory}")

# Call the validation function at the module level to ensure directories are set up
validate_file_paths()
