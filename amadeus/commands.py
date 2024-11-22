import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Optional
import subprocess
import re
import tempfile

import discord
from discord import app_commands
from discord.ext import commands
from tabulate import tabulate

from . import embeds
from . import response


def add_commands(tree: app_commands.CommandTree):
    """
    Adds all commands to the specified command tree.
    :param tree: The tree to add commands to.
    :return: Nothing
    """
    tree.add_command(click)
    tree.add_command(ping)
    tree.add_command(response_group)
    tree.add_command(would_you_rather)
    tree.add_command(rate)
    tree.add_command(conversion_group)
    tree.add_command(dc)


async def send_error(interaction: discord.Interaction, error: str):
    """
    Sends an error embed.
    This uses up the interaction.
    :param interaction: The current interaction.
    :param error: The error message
    :return: Nothing
    """
    embed = embeds.error_embed(error)
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def send_success(interaction: discord.Interaction, message: str):
    """
    Sends a success embed.
    This uses up the interaction.
    :param interaction: The current interaction.
    :param message: The success message
    :return: Nothing
    """
    embed = embeds.success_embed(message)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@app_commands.command(name="ping", description="Plays a lovely game of ping pong and tells you the ping time.")
async def ping(interaction: discord.Interaction):
    dtime = datetime.now(tz=timezone.utc) - interaction.created_at

    await interaction.response.send_message(f"pong motherfucker ({round(dtime.microseconds / 1000, 2)}ms)")


async def autocomplete_response(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    resps = [x.name for x in response.responses][:24]
    resps.append("all")
    return [
        app_commands.Choice(name=resp, value=resp)
        for resp in resps if current.lower() in resp.lower()
    ]


async def autocomplete_state(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    resps = ["react", "message"]
    return [
        app_commands.Choice(name=resp, value=resp)
        for resp in resps if current.lower() in resp.lower()
    ]


async def autocomplete_boolean(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    resps = ["True", "False"]
    return [
        app_commands.Choice(name=resp, value=resp)
        for resp in resps if current.lower() in resp.lower()
    ]


def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 234387706463911939
    return app_commands.check(predicate)

# TODO: Make this per server
@commands.is_owner()
class ResponseGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name='responses', description="Get and modify responses")

    @app_commands.command(name="get", description="Shows all responses and their status")
    @is_me()
    async def get_responses(self, interaction: discord.Interaction):
        table = []

        for r in response.responses:
            table.append([r.name, r.enabled, r.get_state()])

        embed = embeds.default_embed("Responses", f"```{tabulate(table, headers=['Response', 'Enabled', 'Status'])}```")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="set",
                          description="Sets a specified response's status, or all responses status to specified.")
    @app_commands.describe(response_name="The response to set, or \"all\" for all responses.")
    @app_commands.describe(state="The state to set the response to.")
    @app_commands.autocomplete(response_name=autocomplete_response) #TODO: see if there's a way to do this 
    @is_me()
    async def response_set(self, interaction: discord.Interaction, response_name: str, state: str):
        if response_name.lower() != "all":
            resp = response.get_response_by_name(response_name)

            if resp is None:
                await send_error(interaction, f"Cannot find response {response_name}")
                return

            try:
                resp.set_state(state)
            except ValueError as e:
                await send_error(interaction, str(e))
                return

            interaction.client.save_state()
            await send_success(interaction, f"Succesfully set response {response_name} to state {state}")

        else:
            response.set_all_states(defaultdict(lambda: state))

            interaction.client.save_state()
            await send_success(interaction, f"Set all responses to state {state}")

    @app_commands.command(name="enable",
                          description="Enables a specified response, or enables all responses.")
    @app_commands.describe(response_name="The response to enable, or \"all\" for all responses.")
    @app_commands.autocomplete(response_name=autocomplete_response)
    @is_me()
    async def response_enable(self, interaction: discord.Interaction, response_name: str):
        if response_name.lower() != "all":
            r = response.get_response_by_name(response_name)
            if r is None:
                await send_error(interaction, f"Cannot find response {response_name}")
                return

            r.enabled = True
            interaction.client.save_state()
            await send_success(interaction, f"Enabled response {response_name}")

        else:

            response.set_all_enabled(defaultdict(lambda: True))
            interaction.client.save_state()
            await send_success(interaction, f"Enabled all responses")

    @app_commands.command(name="disable",
                          description="Disables a specified response, or disables all responses.")
    @app_commands.describe(response_name="The response to disable, or \"all\" for all responses.")
    @app_commands.autocomplete(response_name=autocomplete_response)
    @is_me()
    async def response_disable(self, interaction: discord.Interaction, response_name: str):
        if response_name.lower() != "all":
            r = response.get_response_by_name(response_name)
            if r is None:
                await send_error(interaction, f"Cannot find response {response_name}")
                return

            r.enabled = False
            interaction.client.save_state()
            await send_success(interaction, f"Disabled response {response_name}")

        else:

            response.set_all_enabled(defaultdict(lambda: False))
            interaction.client.save_state()
            await send_success(interaction, f"Disabled all responses")

response_group = ResponseGroup()

@response_group.error
async def on_response_group_error(interaction: discord.Interaction, error):
    await send_error(interaction, "Hey, only the owner of this bot can use this command!")



#TODO: is this needed? channel permissions are good enough right
class BlacklistGroup(app_commands.Group):

    def __init__(self):
        super().__init__(name="blacklist", description="Manage the channel blacklist")


@app_commands.command(name="wyr",
                      description="Would you rather")
@app_commands.describe(choice1="Choice 1", choice2="Choice 2")
async def would_you_rather(interaction: discord.Interaction, choice1: str, choice2: str):

    await interaction.response.send_message(
        f"would you rather have unlimited {choice1}, but no more {choice2}, or {choice2}, unlimited {choice2}, but no more {choice2}?"
    )


@app_commands.command(name="click", description="Click someone")
@app_commands.describe(member="Who do you want to click?")
async def click(interaction: discord.Interaction, member: discord.Member):

    clicker = embeds.boldifier(interaction.user.name)
    clickee = embeds.boldifier(member.name)

    try:
        times_clicked = interaction.client.click_db[member.id]
    except KeyError:
        times_clicked = 0

    times_clicked += 1

    interaction.client.click_db[member.id] = times_clicked

    interaction.client.save_state()

    embed = embeds.action_embed(f"{clicker} clicks {clickee}. {clickee} has been clicked {times_clicked} time{'s' if times_clicked != 1 else ''}.")

    await interaction.response.send_message(embed=embed)


@app_commands.command(name="rate", description="Rate something.")
@app_commands.describe(something="What you want to rate")
async def rate(interaction: discord.Interaction, something: str):

    def choose_from_md5(md5, md5_index, list):
        return list[int(int(md5[md5_index:md5_index+2], 16) / 256 * len(list))]


    rating_methods = [
        lambda r: f"{round(r * 5, 1)} out of 5 stars.",
        lambda r: f"{round(r * 100)}%.",
        lambda r: f"{round(r * 10)} out of 10.",
    ]

    intros = [
        lambda r: f"{r}, eh?",
        lambda r: f"About {r}?",
        lambda r: f"{r}?",
        lambda r: f"What do I think about {r}?"
    ]

    comments = [
        ["Not looking good.", "Not a big fan.", "It's... something."],
        ["I'm not sure about this.", "Feels a little bit off.", "Could use work"],
        ["Quite average", "Not much to say about it.", "It's alright,"],
        ["Not bad at all.", "Quite good.", "I like it."],
        ["Pretty damn good.", "I'm a big fan.", "Looks great."],
    ]

    md5 = hashlib.md5((something + datetime.today().strftime("%d%m%Y")).encode("utf8")).hexdigest()
    rating = int(md5[0:2], 16) / 256

    intro = choose_from_md5(md5, 2, intros)(something)
    rating_method = choose_from_md5(md5, 4, rating_methods)(rating)
    comment = choose_from_md5(md5, 6, comments[int(rating * len(comments))])

    await interaction.response.send_message(
        embed=embeds.default_embed("", f"{intro} {comment} {rating_method}")
    )

@app_commands.command(name="dc", description="Runs a program in dc")
@app_commands.describe(program="The program to be run", stdin="(Optional) stdin for the program")
async def dc(interaction: discord.Interaction, program: str, stdin: Optional[str]):

    DC_ENCODING = "ascii"
    DC_REGEX = r"![^><=]"

    if re.search(DC_REGEX, program):
        await interaction.response.send_message(
            embed=embeds.dc_embed("dc program contains an invalid command (!)", program, None, embeds.ERROR_COLOR)
        )
        return

    if stdin and "!" in stdin:
        await interaction.response.send_message(
            embed=embeds.dc_embed("stdin contains an invalid character (!)", program, stdin, embeds.ERROR_COLOR)
        )
        return

    with tempfile.NamedTemporaryFile() as fp:

        fp.write(program.encode(DC_ENCODING))
        fp.seek(0)

        try:

            if stdin:
                p = subprocess.run(["dc", "-f", fp.name], input=stdin.encode(DC_ENCODING), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5)
            else: 
                p = subprocess.run(["dc", "-f", fp.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=2)


            await interaction.response.send_message(
                embed=embeds.dc_embed(str(p.stdout, encoding=DC_ENCODING), program, stdin)
            )

        except subprocess.TimeoutExpired:
            await interaction.response.send_message(
                embed=embeds.dc_embed("dc timeout reached (2s)", program, None, embeds.ERROR_COLOR)
            )




class ConversionGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name='convert', description="Converts between different units")

    @staticmethod
    def format_float(f: float):
        return f if int(f) != f else int(f) 

    @app_commands.command(name="ctof", description="Converts celsius to farehnheit")
    @app_commands.describe(temperature="The temperature, in celsius.")
    async def ctof(self, interaction: discord.Interaction, temperature: float):
        new_temperature = round(temperature * 9/5 + 32, 2)
        await interaction.response.send_message(f"{self.format_float(temperature)}°C is {self.format_float(new_temperature)}°F")
    
    @app_commands.command(name="ftoc", description="Converts farenheit to celsius")
    @app_commands.describe(temperature="The temperature, in farenheit.")
    async def ftoc(self, interaction: discord.Interaction, temperature: float):
        new_temperature = round((temperature - 32) * 5/9, 2)
        await interaction.response.send_message(f"{self.format_float(temperature)}°F is {self.format_float(new_temperature)}°C")

conversion_group = ConversionGroup()

