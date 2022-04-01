# ITEE Discord Bot

Role management Discord bot for the ITEE education Discord server. Maintains a list of courses that students can sign up to by reacting to messages sent by the bot. Signing up to a course gives the student the course's associated role.

## Manual Deployment

The bot can be installed and operated manually using command line scripts. Installation is done normally with pip:

    python -m pip install .
    
After installation you can use `iteebot` script to operate the bot. All of these commands take path to configuration file as their second argument. If omitted, it defaults to `./instance/config.json`. The configuration file can be created with the `init-config` command:

    iteebot init-config /path/to/config_file.json/
    
This command writes the factory configuration contents into the designated file, or updates an existing configuration file with fields that have been added to factory configuration after the previous initialization. Creating a full configuration file is optional - factory defaults will also be added to partial configuration files when it's loaded. At minimum you need to provide three configuration values: 

* your Discord access token (TOKEN)
* channel ID for the bot's control channel (CONTROL_CHANNEL)
* and channel ID for the (SIGNUP_CHANNEL)

After configuration you need to initialize the database 

    iteebot init-db /path/to/config_file.json/
    
Then you can run the bot. You can add `--debug` if you want to run in debug mode. Debug mode prints logs into stdout instead of log files.

    iteebot run /path/to/config_file.json/
    
## S2I Deployment

The bot can also run on the Openshift Python 3.9 s2i container image. In order to run the bot in this container image, two secrets and one configmap need to be set up. By default the configmap should dropped into a configuration file (partial is sufficient) in `/etc/iteebot/config.json`. The following environmental variables also need to be set as secrets:

* DISCORD_TOKEN - your Discord access token
* DB_STRING - SQLAlchemy database string

With these configurations the default container image should be able to run the bot.

## Commands

Currently has only one command, `addcourse`. Syntax:

    !addcourse,[role_id],[course_code],[course_name],[course_name_alt] 
    
Where `role_id` is the ID of the Discord role that will be assigned to students who sign up for this course. The remaining fields are used by the bot in the message it sends and should provide informatioon that allows students to find the course they are looking for.



