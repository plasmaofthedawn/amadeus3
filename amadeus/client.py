import pickle
from typing import Any

import discord
from discord import Intents

from . import response, commands


class Amadeus(discord.Client):
    """
    The latest and greatest in Discord bottery.
    """
    def __init__(self, *, intents: Intents, **options: Any):
        self.click_db = {}
        super().__init__(intents=intents, **options)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

        self.retrieve_state()

        try:
            tree = discord.app_commands.CommandTree(self)
            commands.add_commands(tree)
            await tree.sync()
        except discord.errors.ClientException:
            pass

    async def on_message(self, message: discord.Message):

        if message.author.id == self.user.id:
            return

        for i in response.responses:
            if await i.check(message):
                await i.apply(message, self)
                break

    def retrieve_state(self, pickle_name="data.pickle"):
        """
        Retrieves the state from the given pickle.
        This is for saving settings between restarts
        :param pickle_name: The name of the pickle to retrieve the state from
        :return: Nothing
        """

        print("Restoring state")

        try:
            with open(pickle_name, "rb") as f:
                p = pickle.Unpickler(f)
                save = p.load()

            response.set_all_states(save["responses_states"])
            response.set_all_enabled(save["responses_enabled"])

            self.click_db = save["click_db"]

        except Exception:
            print("Restoring failed")

    def save_state(self, pickle_name="data.pickle"):
        """
        Saves the state to the given pickle.
        This is for saving settings between restarts
        :param pickle_name: The name of the pickle to save the state to
        :return: Nothing
        """

        print("Saving state")

        save = {
            "responses_states": response.get_all_states(),
            "responses_enabled": response.get_all_enabled(),
            "click_db": self.click_db
        }

        with open("data.pickle", "wb") as f:
            p = pickle.Pickler(f)

            p.dump(save)


def create_client() -> Amadeus:
    """
    Creates a client with the default settings
    :return: The client.
    """
    intents = discord.Intents.default()
    intents.message_content = True

    client = Amadeus(intents=intents)

    return client
