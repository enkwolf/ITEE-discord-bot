"""
Configuration utilities for ITEEBot. Configuration is initialized by
writing the factory configuration into a file. This can also be used to 
update an existing configuration file with default values. 

When configuration is loaded, it is also always updated on top of the factory
configuration to ensure all options have been set. So technically local 
configuration files do not need to be complete. Using the initialization is
simply a utility for making a new editable configuration file that has all
options included.
"""

import json
import os

FACTORY = {
    "TOKEN": "insert-token-here",
    "DB": "sqlite:///botdata.db",
    "CONTROL_CHANNEL": 0,
    "SIGNUP_CHANNEL": 0,
    "COMMAND_SEP": ",",
    "MESSAGES": {
        "SIGNUP": "{code} {name_en} / {name_fi}"
    },
    "LOG": {
        "FILE": "instance/log/iteebot.log",
        "ROTATE": ("d", 31),
        "BACKUPS": 6
    }
}

def write_config_file(path):
    """
    Writes factory configuration to path. If the file exists, its contents are
    only updated from the factory configuration, options that have been set
    in the file are retained. Can be used to create a config file template when
    installing the bot, and also to update an existing configuration file to
    include options that have been added in an update.
    
    * path (str) - path to the configuration file
    """

    try:
        config = load_config(path)
    except FileNotFoundError:
        print("No existing configuration, writing fresh file")
        config = FACTORY.copy()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def load_config(path):
    """
    Loads configuration from path. The loaded configuration is updated on top
    top of the factory configuration in this file to ensure that the resulting
    dictionary has all of the required keys.

    * path (str) - path to the configuration file
    """

    with open(path, encoding="utf-8") as f:
        local = json.load(f)
    
    config = FACTORY.copy()
    config.update(local)
    return config
