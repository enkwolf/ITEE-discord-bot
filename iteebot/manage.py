"""
Command line management utilities for ITEEBot. This module's command line
interface will act as the bot's entry point when installed.
"""

import click
from . import configurator as conf
from . import database as db
from .bot import ITEEBot

@click.group()
def cli():
    pass

@click.command("init-config")
@click.argument(
    "config_path",
    default="instance/config.json",
    type=click.Path()
)
def create_config(config_path):
    """
    Command for writing or updating a configuration file. Configuration file
    path will default to instance/config.json. 
    
    * config_path (str) - Path to the configuration file
    
    Example:
    iteebot init-config /home/donkey/.iteebot/config.json
    """
    
    conf.write_config_file(config_path)
    
@click.command("init-db")
@click.argument(
    "config_path",
    default="instance/config.json",
    type=click.Path(exists=True)
)
def init_db(config_path):
    """
    Initializes a database to the location defined in the configuration's DB
    option. 

    * config_path (str) - Path to the configuration file
    
    Example:
    iteebot init-db /home/donkey/.iteebot/config.json
    """

    config = conf.load_config(config_path)
    db.init_db(config["DB"])

@click.command("run")
@click.option("--debug", default=False, help="Run in debug mode")
@click.argument(
    "config_path",
    default="instance/config.json",
    type=click.Path(exists=True)
)
def run(debug, config_path):
    """
    Runs the bot using configuration frome the specific location (or default 
    of instance/config.json). Optional debug flag can be set to run in debug
    mode, which will print logs to stdout instead of using log files.

    * config_path (str) - Path to the configuration file
    * debug (bool) - Run in debug mode
    
    Example:
    iteebot run --debug /home/donkey/.iteebot/config.json
    """

    config = conf.load_config(config_path)
    bot = ITEEBot(config, debug=debug)
    bot.run()

cli.add_command(create_config)
cli.add_command(init_db)
cli.add_command(run)

if __name__ == "__main__":
    cli()
