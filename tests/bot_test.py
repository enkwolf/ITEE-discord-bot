"""
Simple test suite mostly for checking that nothing was broken when modifying
the code. As it is currently not possible to test communication with Discord,
these tests only focus on internal functionality. In order to bypass the need
for a connection to Discord, a mockup version of the ITEEBot class is tested
instead. This class has mockup methods for the interface functions the bot is
trying to call.
"""

import json
import os
import pytest
import random
import tempfile
from sqlalchemy.orm import Session
from click.testing import CliRunner
from iteebot import database
from iteebot.configurator import FACTORY, load_config
from iteebot.manage import init_db, create_config

from tests.mocks import *

TEST_CHANNEL = 7357
TEST_MESSAGE = 4451

@pytest.fixture
def config_path():
    """
    Base fixture that creates a configuration file with the test configuration
    and a database file for testing. Both files are properly cleaned up.
    """

    cfg_fd, cfg_name = tempfile.mkstemp(text=True)
    db_fd, db_name = tempfile.mkstemp()
    local = {
        "DB": f"sqlite:///{db_name}",
        "SIGNUP_CHANNEL": TEST_CHANNEL,
    }
    with os.fdopen(cfg_fd, "w") as cfg_file:
        json.dump(local, cfg_file)
    yield cfg_name
    os.close(db_fd)
    os.unlink(db_name)
    os.unlink(cfg_name)

@pytest.fixture
def bot(config_path):
    """
    Bot fixture for getting an instance of the bot. A derived MockClient class
    is used instead of ITEEBot.
    
    * config_path (fixture) - path to the test configuration for loading it
    """

    config = load_config(config_path)
    database.init_db(config["DB"])
    bot = MockClient(config, debug=True)
    bot.run()
    yield bot

def populate_db(engine):
    """
    Populates the database for tests that need existing course data.
    
    * engine - SQLAlchemy engine object
    """

    with Session(engine) as s:
        course = database.Course(
            code="7357",
            message_id=TEST_MESSAGE,
            role_id=1
        )
        s.add(course)
        s.commit()

def test_config_write(config_path):
    """
    Tests that the init-config command works
    
    * config_path (fixture) - path to the test configuration for loading it    
    """

    runner = CliRunner()
    result = runner.invoke(create_config, [config_path])
    assert result.exit_code == 0

def test_db_init(config_path):
    """
    Tests that the init-db command works
    
    * config_path (fixture) - path to the test configuration for loading it    
    """
    runner = CliRunner()
    result = runner.invoke(init_db, [config_path])
    assert result.exit_code == 0
    
@pytest.mark.asyncio
async def test_command_test(bot):
    """
    Tests the !test command.
    
    * bot (fixture) - configured testable bot object
    """
    msg = MockMessage(1, "!test")
    await bot._parse_command(msg)
    
@pytest.mark.asyncio
async def test_command_addcourse(bot):
    """
    Tests the !addcourse command. Verifies that a message is sent to a mock
    channel, and that database entry for the course is created.
    
    * bot (fixture) - configured testable bot object
    """
    code = "test"
    name_fi = "testikurssi"
    name_en = "test course"
    msg = MockMessage(2, f"!addcourse,123,{code},{name_en},{name_fi}")
    channel = bot.create_channel(TEST_CHANNEL)
    await bot._parse_command(msg)
    with Session(bot._engine) as s:
        assert s.query(database.Course).count() == 1

@pytest.mark.asyncio
async def test_reaction(bot):
    """
    Tests adding and removing a reaction to the test course's signup message.
    Uses various mockups to allow the bot to do things against them without
    connecting to Discord.
    
    * bot (fixture) - configured testable bot object
    """
    populate_db(bot._engine)
    msg = MockMessage(TEST_MESSAGE, "placeholder")
    guild = bot.create_guild(1)
    role = guild.create_role(1)
    member = guild.create_member(1)
    reaction = MockReactionEvent(msg, TEST_CHANNEL, guild.id, member)
    await bot.on_raw_reaction_add(reaction)
    assert role in member.roles
    await bot.on_raw_reaction_remove(reaction)
    assert role not in member.roles
