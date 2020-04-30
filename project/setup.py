from setuptools import setup, find_packages
setup(
    name = "project",
    version = "0.1",
    packages = find_packages(),
    entry_points = {
        "console_scripts": [
            "project = project:main",
        ],
        "project.plugins": [
            "Plugin1_1 = project:Plugin1_1",
        ]
    }
)
