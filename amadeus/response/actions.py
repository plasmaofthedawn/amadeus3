import random
import re
from typing import Union, List, Callable

import discord

from amadeus import embeds

class Action:
    """
    Class that holds an action that a bot can take.
    """

    async def apply(self, msg: discord.Message, bot: discord.Client):
        """
        Runs this action on a bot.
        :param msg: The message that this is being sent to
        :param bot: The client to be run on.
        :return: Nothing
        """
        raise NotImplemented


class LiteralSendAction(Action):
    """
     An action that sends a specific message.
     e.g. sending "you're welcome."
     """

    def __init__(self, phrase):
        """
        Creates a new LiteralSendAction
        :param phrase: The phrase that will be sent by this action
        """
        self.phrase = phrase

    async def apply(self, msg: discord.Message, bot: discord.Client):
        await msg.channel.send(self.phrase)


class RegexSendAction(Action):
    """
    An action that sends the original message with a re.sub applied to it.
    e.g. "i'm gay" becoming "hi gay, i'm dad"
    """

    def __init__(self, regex, replacement, flags=re.IGNORECASE | re.MULTILINE):
        """
        Creates a new RegexSendAction
        :param regex: The regex to be fed into re.sub
        :param replacement: The replacement to be fed into re.sub
        :param flags: The flags to be used in re.sub
        """
        self.regex = regex
        self.replacement = replacement
        self.flags = flags

    async def apply(self, msg: discord.Message, bot: discord.Client):
        message = re.sub(self.regex, self.replacement, msg.content, flags=self.flags)
        await msg.channel.send(message)


class RandomLiteralAction(Action):
    """
    An action that says one of a random literals.
    e.g. "uwu" or "owo"

    Any literal that is a function will be evaluated with the message as an argument.
    """

    def __init__(self, literals: List[Union[str, Callable[[discord.Message], str]]]):
        """
        Create a new RandomLiteralAction
        :param literals: A list of literals or functions to be evaluated. Functions will be given the message as an argument, and should return a string.
        """
        self.literals = literals

    async def apply(self, msg: discord.Message, bot: discord.Client):
        literals = [x if type(x) is str else x(msg) for x in self.literals]
        await msg.channel.send(random.choice(literals))


class ReactAction(Action):
    """
    An action that reacts to the message with an emoji.
    This only supports server emojis, and not base emojis.
    TODO: fix this ^
    """
    def __init__(self, emoji: int):
        """
        Creates a new ReactAction
        :param emoji: the id of the emoji to react.
        """
        self.emoji = emoji

    async def apply(self, msg: discord.Message, bot: discord.Client):
        await msg.add_reaction(bot.get_emoji(self.emoji))


class SendRandomActionEmbedAction(Action):
    """
    An action that gives a random possibility from a list, with an optional custom embed generator and name modifier
    Possibilties are strings that get formatted with two things, the actioner (0) and the actionee (1).
    """

    def __init__(self, possibilities: List[str], embed_generator=embeds.action_embed, name_modifier=embeds.boldifier):

        self.possibilities = possibilities
        self.embed_generator = embed_generator
        self.name_modifier = name_modifier

    async def apply(self, msg: discord.Message, bot: discord.Client):

        actioner = self.name_modifier(msg.author.name)
        actionees = [x.name for x in msg.mentions]

        if len(actionees) == 0:
            actionees = msg.content.split(" ")[1:]

        if len(actionees) == 0:
            actionees = [bot.user.name]

        out = "\n\n".join(
            [
                random.choice(self.possibilities).format(actioner, self.name_modifier(x)) for x in actionees
            ]
        )

        await msg.channel.send(embed=self.embed_generator(out))