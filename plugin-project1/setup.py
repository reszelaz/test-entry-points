from setuptools import setup, find_packages


setup(
    name="plugin-project1",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "project.plugins": [
            "Plugin1_1 = plugin_project1:Plugin1_1",
            "Plugin1_2 = plugin_project1:Plugin1_2",
            "Plugin1_3 = plugin_project1:Plugin1_3"
        ]
    }
)
