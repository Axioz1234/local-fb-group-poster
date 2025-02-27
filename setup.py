from setuptools import setup, find_packages

setup(
    name="local-fb-group-poster",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "customtkinter",
        "selenium",
    ],
    entry_points={
        'console_scripts': [
            'local-fb-group-poster=facebook_poster.main:main',
        ],
    },
)
