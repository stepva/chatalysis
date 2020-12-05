# Standard library imports
import os.path
# Third party imports
from setuptools import setup
# Application imports
from chatalysis import version


with open('README.md') as file:
    readme = file.read()

with open('requirements.txt') as file:
    requirements = file.read().splitlines()


setup(
    name="chatalysis",
    version=version,
    description="Chatalysis visualises stats from your Facebook Messenger chats",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/stepva/chatalysis",
    packages=["chatalysis"],
    include_package_data=True,
    install_requires=requirements,
    entry_points={"console_scripts": ["chatalysis=chatalysis.__main__:main"]},
)