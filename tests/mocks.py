"""
This module includes mockups that simulate the discord.py interface for the
parts needed by the bot. 
"""

import random
from iteebot.bot import ITEEBot

class MockMessage:
    """
    Mockup for Message.
    """
    
    def __init__(self, msg_id, content):
        self.content = content
        self.id = msg_id


class MockChannel:
    """
    Mockup for channel. Has a mockup send method that appends messages sent by
    the bot to a list, making them accessible for verification.
    """
    
    def __init__(self, channel_id):
        self.id = channel_id
        self._log = []

    async def send(self, message):
        """
        Simulates sending a message, by appending a message objects to the
        channel's log list.
        """
    
        msg_obj = MockMessage(
            random.randint(1, 1000),
            message
        )
        self._log.append(msg_obj)
        return msg_obj


class MockReactionEvent:
    """
    Mockup for RawReactionEvent. Includes all attributes that are used when the
    bot responds to reactions by adding/removing roles.
    """
    
    def __init__(self, message, channel_id, guild_id, member):
        self.message_id = message.id
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user_id = member.id
        self.member = member


class MockRole:
    """
    Mockup class for simulating roles.
    """

    def __init__(self, role_id):
        self.id = role_id


class MockGuild:
    """
    Mockup for guild objects. Has methods for adding roles and members, as well
    as the get methods that are part of a real guild object's interface.
    """
    
    def __init__(self, guild_id):
        self.id = guild_id
        self._roles = {}
        self._members = {}
        
    def create_role(self, role_id):
        """
        Creates and returns a new mock role object with the given ID. The role
        is stored internally with its ID in the roles dictionary.
        
        * role_id (int) - ID number for the new role
        """
    
        role = MockRole(role_id)
        self._roles[role_id] = role
        return role
        
    def create_member(self, user_id):
        """
        Creates and returns a mock member object with the given ID. The member is
        is stored internally with its ID in the members dictionary.
        
        * user_id (intt) - ID number for the new member
        """
        
        member = MockMember(user_id)
        self._members[user_id] = member
        return member
        
    def get_role(self, role_id):
        """
        Returns a role object that corresponds to role_id
        
        * role_id (int) - ID number for role lookup
        """
        return self._roles[role_id]
    
    def get_member(self, user_id):
        """
        Returns a member object that corresponds to user_id
        
        * user_id (int) - ID number for member lookup
        """
    
        return self._members[user_id]


class MockMember:
    
    def __init__(self, user_id):
        self.roles = set()
        self.id = user_id
        
    async def add_roles(self, role):
        self.roles.add(role)
        
    async def remove_roles(self, role):
        self.roles.remove(role)


class MockClient(ITEEBot):
    
    _running = False
    
    def run(self, *args, **kwargs):
        if "TOKEN" in self._cfg:
            self._running = True
            self._channels = {}
            self._guilds = {}
    
    def create_channel(self, channel_id):
        channel = MockChannel(channel_id)
        self._channels[channel_id] = channel
        return channel
    
    def create_guild(self, guild_id):
        guild = MockGuild(guild_id)
        self._guilds[guild_id] = guild
        return guild
    
    def get_channel(self, channel_id):
        return self._channels[channel_id]

    def get_guild(self, guild_id):
        return self._guilds[guild_id]

