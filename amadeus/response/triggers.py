import re
from typing import List

import discord


class Trigger:

    async def check(self, msg: discord.Message) -> bool:
        """
        Checks to see if a response should be applied to a message, and then gives an appropriate action for the bot to execute.
        :param msg: The message that is being responded to
        :return: Whether the attached action should be executed or not
        """

        raise NotImplemented


class LiteralsTrigger(Trigger):
    """
    A trigger to a specific messages.
    e.g. a message saying "thanks bot" or "thank you bot"

    Does not set a result.
    """

    def __init__(self, phrases: List[str], contains=False, case_sensitive=True):
        """
        Creates a new LiteralsTrigger
        :param phrases: a list of phrases that will trip the trigger
        :param contains: whether it has to be an exact match, or if the message nearly has to contain a phrase
        :param case_sensitive: whether it has to match case exactly with the specified phrase.
        """
        self.phrases = phrases
        self.contains = contains
        self.case_sensitive = case_sensitive

        if not case_sensitive:
            self.phrases = [x.lower() for x in phrases]

    async def check(self, msg: discord.Message) -> bool:

        content = msg.content

        if not self.case_sensitive:
            content = content.lower()

        for phrase in self.phrases:
            if (not self.contains and phrase == content) or phrase in content:
                return True
        return False


class RegexTrigger(Trigger):
    """
    A trigger that trips when a message matches a regex.
    """

    def __init__(self, regex, flags=re.IGNORECASE | re.MULTILINE):
        """
        Creates a new RegexTrigger
        :param regex: The regex to search the message for
        :param flags: Flags to use in the re.search
        """
        self.regex = regex
        self.flags = flags

    async def check(self, msg: discord.Message) -> bool:
        return re.search(self.regex, msg.content, flags=self.flags) is not None


class LastAuthorTrigger(Trigger):
    """
    A trigger that trips when the previous message sent was sent by a certain user.
    """
    def __init__(self, author: int):
        """
        Creates a new LastAuthorTrigger
        The trigger is tripped when the previous message was sent by the given author.
        :param author: The id of the author who should trip this trigger.
        """
        self.author = author

    async def check(self, msg: discord.Message) -> bool:
        history = msg.channel.history(limit=2)
        await anext(history)

        last_message = await anext(history)

        return False if last_message is None else last_message.author.id == self.author


class OrTrigger(Trigger):
    """
    A trigger that trips when any of the triggers given to it trips.
    """
    def __init__(self, *args: Trigger):
        """
        Creates a new OrTrigger
        :param args: List of triggers to watch
        """
        self.triggers = args

    async def check(self, msg: discord.Message) -> bool:
        for i in self.triggers:
            if await i.check(msg):
                return True

        return False


class AndTrigger(Trigger):
    """
    A trigger that trips when all the triggers given to it trips.
    """
    def __init__(self, *args: Trigger):
        """
        Creates a new AndTrigger
        :param args: List of triggers to watch
        """
        self.triggers = args

    async def check(self, msg: discord.Message) -> bool:
        for i in self.triggers:
            if not await i.check(msg):
                return False

        return True


class MentionsTrigger(Trigger):
    """
    A trigger that trips when specified user is mentioned, or optionally if the message is replying to a message by the user.
    """
    def __init__(self, ping_id: int, reply=True):
        """
        Creates a new MentionsTrigger
        :param ping_id: The id of the user of which pings should watch for
        :param reply: Whether the trigger should also trip if the user was replied to
        """
        self.ping_id = ping_id
        self.reply = reply

    async def check(self, msg: discord.Message) -> bool:
        if self.reply:
            return self.ping_id in msg.raw_mentions or (msg.reference is not None and type(msg.reference.resolved) is not discord.DeletedReferencedMessage and msg.reference.resolved.author.id == self.ping_id)
        return self.ping_id in msg.raw_mentions
