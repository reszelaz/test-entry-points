from setuptools import setup, find_packages
from project import find_plugins_ep


setup(
    name="plugin-project2",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "project.plugins": find_plugins_ep()
    }
)
