from setuptools import find_packages, setup

setup(
    name="ITEE-bot",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "sqlalchemy",
        "discord",
        "click"
    ],
    extras_require=[
        "pytest",
        "pytest-asyncio"
    ]
    entry_points={
        "console_scripts": [
            "iteebot=iteebot.manage:cli"
        ]
    },
)
