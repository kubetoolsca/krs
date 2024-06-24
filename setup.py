# import os
# from setuptools import setup, find_packages

# # Read the requirements.txt file for dependencies
# with open('krs/requirements.txt') as f:
#     requirements = f.read().splitlines()

# # Read the README file for long description
# with open('README.md') as f:
#     long_description = f.read()

# setup(
#     name='krs',
#     version='0.1.0',
#     description='Kubernetes Recommendation Service with LLM integration',
#     long_description=long_description,
#     long_description_content_type='text/markdown',
#     author='Abhijeet Mazumdar, Karan Singh, Adesoji Alu & Ajeet Singh Raina',
#     author_email='abhijeet@kubetools.ca, karan@kubetools.ca, ajeet@kubetools.ca',
#     url='https://github.com/KrsGPTs/krs',
#     packages=find_packages(),
#     include_package_data=True,
#     install_requires=requirements,
#     entry_points={
#         'console_scripts': [
#             'krs=krs.krs:app',  # Adjust the module and function path as needed
#         ],
#     },
#     classifiers=[
#         'Programming Language :: Python :: 3',
#         'License :: OSI Approved :: MIT License',
#         'Operating System :: OS Independent',
#     ],
#     python_requires='>=3.6',
#     package_data={
#         'krs': [
#             'data/*.json',
#             'data/*.yml',
#             'data/*.pkl',
#             'requirements.sh',
#             'requirements.bat',
#             # Add other patterns as needed
#         ],
#     },
# )



from setuptools import setup, find_packages
import os
import sys
from subprocess import check_call

# Read the requirements.txt file for dependencies
with open('krs/requirements.txt') as f:
    requirements = f.read().splitlines()

# Define a function to install OS-specific dependencies
def install_os_specific_requirements():
    if sys.platform.startswith('linux'):
        check_call(['bash', 'krs/requirements.sh'])
    elif sys.platform.startswith('win'):
        check_call(['cmd', '/c', 'krs/requirements.bat'])

# Call the function to install OS-specific dependencies
install_os_specific_requirements()

setup(
    name='krs',
    version='0.1.0',
    description='Kubernetes Recommendation Service with LLM integration',
    author='Abhijeet Mazumdar , Karan Singh & Ajeet Singh Raina',
    author_email='abhijeet@kubetools.ca, karan@kubetools.ca, ajeet@kubetools.ca',
    url='https://github.com/KrsGPTs/krs',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'krs=krs.krs:app',  # Adjust the module and function path as needed
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
