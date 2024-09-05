from setuptools import setup, find_packages

# Read the requirements.txt file for dependencies
with open('krs/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='krs',
    version='0.1.0',
    description='Kubernetes Recommendation Service with LLM integration',
    author='Abhijeet Mazumdar , Karan Singh & Ajeet Singh Raina',
    author_email='abhijeet@kubetools.ca, karan@kubetools.ca, ajeet@kubetools.ca',
    url='https://github.com/kubetoolsca/krs',
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
