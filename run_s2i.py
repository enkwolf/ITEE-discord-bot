import os
import iteebot.database as db
from iteebot.bot import ITEEBot
from iteebot.configurator import load_config

if __name__ == "__main__":
    config = load_config(os.environ["CONFIG_PATH"])
    
    # add values from secrets
    config["TOKEN"] = os.environ["DISCORD_TOKEN"]
    config["DB"]= os.environ["DB_STRING"]
    
    db.init_db(config)
    bot = ITEEBot(config)
    bot.run()
    
