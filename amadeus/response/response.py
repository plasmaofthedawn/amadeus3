from .actions import *
from .triggers import *

import random

class Response:
    """
    A response is a Trigger and an Action, along with tools to enable/disable the response.
    Otherwise, it's functionally a container class for a Trigger Action pair.
    """
    def __init__(self, trigger: Trigger, action: Action, name):
        """
        Creates a new Response
        :param trigger: The trigger to be used
        :param action: The action to be used
        :param name: A unique name for the Response.
        Note that names are not case-sensitive and uniqueness is not checked for
        """
        self.trigger = trigger
        self.action = action
        self.name = name
        self.enabled = True

    async def check(self, msg: discord.Message):
        """
        Checks a message to see if it trips a trigger
        :param msg: The discord message to be checked
        :return: False if not enabled, else the result of the trigger being checked.
        """
        if not self.enabled:
            return False
        return await self.trigger.check(msg)

    async def apply(self, msg, bot):
        """
        Applies the associated action.
        :param msg: The message that this is being sent to
        :param bot: The client to be run on.
        :return: Nothing
        """
        await self.action.apply(msg, bot)

    def get_state(self):
        """
        Returns the current state of this Response.
        This is unused in the base Response, but can be used in subclasses to allow for on the fly customization.
        :return: The state of this response
        """
        # TODO: make this a NotImplmentedException and add the proper handling to the command
        return "N/A"

    def set_state(self, state):
        """
        Sets the current state of this Response.
        Returns the current state of this Remodsponse.
        This is unused in the base Response, but can be used in subclasses to allow for on the fly customization.
        :param state: The state to set this Response to.
        :return: Nothing
        """
        raise ValueError("Cannot set a state for this response.")


class SendOrReactResponse(Response):
    """
    A Response superclass that allows for on the fly configuration between two actions: a ReactAction and a
    LiteralSendAction
    """
    def __init__(self, trigger: Trigger, message: str, emoji_id: int, name, default="message"):
        """
        Create a new SendOrReactResponse
        :param trigger: The trigger for this Response
        :param message: The message for the LiteralSendAction
        :param emoji_id: The emoji for the ReactAction
        :param name: A unique name for the Response.
        Note that names are not case-sensitive and uniqueness is not checked for
        :param default: The default state of this Response.
        """
        super().__init__(trigger, None, name)
        self.message = message
        self.emoji_id = emoji_id

        self.send_message_action = LiteralSendAction(message)
        self.react_action = ReactAction(emoji_id)

        self.state = default

        if default == "message":
            self.action = self.send_message_action
        elif default == "react":
            self.action = self.react_action
        else:
            raise ValueError(f"Default can only be either \"message\" or \"react\", not {default}")

    def get_state(self):
        return self.state

    def set_state(self, state):

        if state == "react":
            self.action = self.react_action
        elif state == "message":
            self.action = self.send_message_action
        else:
            raise ValueError(f"State can only be either \"message\" or \"react\".")

        self.state = state

class RandomChanceResponse(Response):
    """
    A response that has a random chance to apply it's action when triggered.
    The chance of the randomness is configurable on the fly.
    """

    def __init__(self, trigger: Trigger, action: Action, name, default=0.5):
        super().__init__(trigger, action, name)

        self.chance = default


    def get_state(self):
        return str(self.chance)

    def set_state(self, state):

        try:
            new_chance = float(state)
        except ValueError:
            raise ValueError(f"{state} is not a valid state for this response. It has to be a floating point number.")

        if new_chance < 0 or new_chance > 1:
            raise ValueError(f"{new_chance} is not a valid probability. It needs to be inbetween 0 and 1 (inclusive).")

        self.chance = new_chance

    async def apply(self, msg, bot):        

        """
        Applies the associated action.
        :param msg: The message that this is being sent to
        :param bot: The client to be run on.
        :return: Nothing
        """

        if random.random() < self.chance:
            await super().apply(msg, bot)

