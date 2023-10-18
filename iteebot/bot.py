"""
ITEEBot is a role management bot used in the University of Oulu ITEE
education Discord server to allow users to sign up for course areas.
It holds an internal database of registered courses, each with an assigned
role ID, and a signup message ID. When user reacts to the signup message, the
bot will assign the associated role for that user. When they remove reaction,
the bot will remove the associated role.
"""

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

import discord
from sqlalchemy.orm import Session

from . import database as db

class ITEEBot(discord.Client):
    """
    This class extends discord.py Client. Primary addition is the ability to
    hold two internal objects: a configuration dictionary, and SQLAlchemy
    engine object for database access. These are held in internal attributes
    _cfg and _engine, respectively.
    """
    
    def __init__(self, config, *args, debug=False, **kwargs):
        """
        Initializes the bot using options from a configuration file. Also
        initializes logging based on the debug argument, using stdout if it is
        True, or a time rotating logger otherwise.
        
        Intents are currently hard-coded based on what are needed for the bot's
        current features.
        
        * config (dict) - configuration dictionary from the configurator module
        * debug (bool) - run in debug mode
        """
    
        self._cfg = config
        intents = discord.Intents(
            members=True,
            messages=True,
            reactions=True,
            guilds=True
        )
        self._engine = db.get_engine(config["DB"])
        if debug:   
            logging.basicConfig(level=logging.DEBUG)
        else:
            os.makedirs(os.path.dirname(config["LOG"]["FILE"]), exist_ok=True)
            rotator = TimedRotatingFileHandler(
                config["LOG"]["FILE"],
                when=config["LOG"]["ROTATE"][0],
                interval=config["LOG"]["ROTATE"][1],
            )
            logging.basicConfig(
                format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                handlers=[rotator],
                level=logging.INFO
            )
        super().__init__(*args, intents=intents, **kwargs)
    
    def run(self, *args, **kwargs):
        """
        Runs the bot, with access token digged up from the configuration.
        """
    
        super().run(self._cfg["TOKEN"], *args, **kwargs)
        
    async def on_raw_reaction_add(self, event):
        """
        Uses the reaction event's message ID to find the course associated
        with the reacted message. If the course is found, the associated role
        is assigned to the user who triggered the reaction event.
        
        Reactions on channels other than the designated singup channel are 
        ignored.
       
        * event (RawReactionEvent) - reaction event from discord.py
        """
        
        if event.channel_id != self._cfg["SIGNUP_CHANNEL"]:
            return

        with Session(self._engine) as s:
            course = s.query(db.Course).filter_by(
                message_id=event.message_id
            ).first()
            if not course:
                return
        
        guild = self.get_guild(event.guild_id)
        role = guild.get_role(course.role_id)
        await event.member.add_roles(role)

    async def on_raw_reaction_remove(self, event):
        """
        Uses the reaction event's message ID to find the course associated
        with the reacted message. If the course is found, the associated role
        is removed from the user who triggered the reaction event.

        Reactions on channels other than the designated singup channel are 
        ignored.

        * event (RawReactionEvent) - reaction event from discord.py
        """

        if event.channel_id != self._cfg["SIGNUP_CHANNEL"]:
            return

        with Session(self._engine) as s:
            course = s.query(db.Course).filter_by(
                message_id=event.message_id
            ).first()
            if not course:
                return
        
        guild = self.get_guild(event.guild_id)
        role = guild.get_role(course.role_id)
        member = guild.get_member(event.user_id)
        await member.remove_roles(role)

    async def on_error(self, event, *args, **kwargs):
        """
        Logs errors. 
        
        * event (str) - name of the event that caused the error
        """
    
        etype, evalue, etrace = sys.exc_info()
        logging.error(f"Error processing event {event} with arguments")
        logging.error(",".join(repr(arg) for arg in args))
        logging.error(",".join(f"{key!r}: {val!r}" for key, val in kwargs))
        logging.error(f"{etype} - {evalue}")

    async def on_ready(self):
        """
        Simply logs the ready status for debug purposes.
        """
        
        logging.info("Online") 

    async def on_message(self, message):
        """
        Handles messages from other users. Currently this is a command handler.
        Messages are only parsed if they were sent to the designated control
        channel.
        
        * message (Message) - a discord.py message object
        """
        
        if message.author == self.user:
            return
            
        if message.channel.id == self._cfg["CONTROL_CHANNEL"]:
            logging.debug("Command channel event")
            await self._parse_command(message)
        
    async def _parse_command(self, message):
        """
        Parses messages that are regarded commands, currently marked with 
        exclamation mark prefix (!). The separator is configurable in order to
        account for different use cases without adding escape mechanisms to
        the command syntax.
        
        Command handlers are looked up with getattr and need to be named in
        the _{command_keyword}_command pattern.

        * message (Message) - a discord.py message object
        """
    
        content = message.content.lstrip("<@0123456789> ")
        logging.debug(content)

        if not content.startswith("!"):
            return
        command, *args = content.lstrip("!").split(
            self._cfg["COMMAND_SEP"]
        )
        logging.info(f"Received command {command} with args:")
        logging.info(self._cfg["COMMAND_SEP"].join(args))
        handler = getattr(self, f"_{command}_handler", self._invalid_command)
        await handler(message, *args)
        
    async def _invalid_command(self, message, *args):
        """
        Default handler for commands that are not supported. Logs the attempted
        command as a warning.

        * message (Message) - a discord.py message object
        """
    
        logging.warning("Reveived invalid command")
        logging.warning(message.content)
        
    async def _test_handler(self, message, *args):
        """
        A simple test command handler for testing that commands go through.

        * message (Message) - a discord.py message object
        """
    
        logging.debug("Received test command")

    async def _addcourse_handler(self, 
                           message,
                           role_id,
                           course_code,
                           course_name_en,
                           course_name_fi):
        """
        Handler for the addcourse command. Upon receiveing this command, the
        bot will post a new signup message to the desingated signup channel,
        using the message template from configuration. After confirming that
        the message has been posted, the bot creates a database record for the
        new course that associates the message ID with the course, and 
        especially course's role ID. 
        
        * message (Message) - a discord.py message object
        * role_id (int) - ID of an existing role
        * course_code (str) - course's official code
        * course_name_en (str) - course's name in English
        * course_name_fi (str) - course's name in Finnish
        """
        
        channel = self.get_channel(self._cfg["SIGNUP_CHANNEL"])
        signup = await channel.send(
            self._cfg["MESSAGES"]["SIGNUP"].format(
                code=course_code,
                name_en=course_name_en,
                name_fi=course_name_fi,
            )
        )
        with Session(self._engine) as s:
            course = db.Course(
                code=course_code,
                name_fi=course_name_fi,
                name_en=course_name_en,
                role_id=int(role_id),
                message_id=signup.id
            )
            s.add(course)
            s.commit()
