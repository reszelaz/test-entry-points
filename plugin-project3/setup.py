from setuptools import setup, find_packages


setup(
    name="plugin-project3",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "project.plugins":
        [
            "Plugin3_1 = plugin_project3.plugin_module:Plugin3_1"
        ]
    }
)
