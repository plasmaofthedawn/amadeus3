import discord


DEFAULT_COLOR = 0x521414
ERROR_COLOR = 0xab0306
SUCCESS_COLOR = 0x079100

def default_embed(title: str, msg: str, color=DEFAULT_COLOR):
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
    return default_embed("Error", error, color=ERROR_COLOR)


def success_embed(message: str):
    """
    Creates an embed to report a success.
    :param message: The success message.
    :return: The embed.
    """
    return default_embed("Success", message, color=SUCCESS_COLOR)


def boldifier(x: str):
    return f"**{x}**"


def action_embed(text):
    return default_embed(
        "", text
    )

def dc_embed(output: str, command: str, stdin: str | None, color=DEFAULT_COLOR):

    embed = discord.Embed()

    embed.title = "dc"
    embed.description = "```" + output + "```"
    embed.color = color

    embed.add_field(name="command", value="`"+command+"`", inline=True)

    if stdin:
        embed.add_field(name="stdin", value="`"+stdin, inline=True)

    return embed
