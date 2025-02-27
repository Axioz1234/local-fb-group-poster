from setuptools import setup, find_packages

setup(
    name="local-fb-group-poster",
    version="0.1",
    packages=["facebook_poster"],
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
    ],
    entry_points={
        'console_scripts': [
            'local-fb-group-poster=facebook_poster.main:FacebookPoster().run',
        ],
    },
)
