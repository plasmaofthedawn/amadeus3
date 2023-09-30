import random

import discord


def default_embed(title: str, msg: str, color=0x521414):
    """
    Creates a mostly empty embed.
    This function will mostly be used by other embed generators.
    :param title: The title of the embed.
    :param msg: The content of the embed.
    :param color: The color of the embed.
    :return: The embed. Shocking.
    """
    embed = discord.Embed()
    embed.title = title
    embed.description = msg
    embed.colour = color

    # embed.set_footer(text="by plasmaofthedawn")

    return embed


def error_embed(error: str):
    """
    Creates an embed to report an error.
    :param error: The error string.
    :return: The embed.
    """
    return default_embed("Error", error, color=0xab0306)


def success_embed(message: str):
    """
    Creates an embed to report a success.
    :param message: The success message.
    :return: The embed.
    """
    return default_embed("Success", message, color=0x079100)


def boldifier(x: str):
    return f"**{x}**"


def action_embed(text):
    return default_embed(
        "", text
    )
