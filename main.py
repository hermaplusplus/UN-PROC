import discord
from discord import app_commands
from discord import ui
from discord import utils

from typing import Optional

from datetime import datetime

import time

import json

import requests

SETTINGS = json.load(open("settings.json", "r"))

from byond2json import player2dict as getPlayerData

PRIORITY_GUILDS = [discord.Object(id=342787099407155202), discord.Object(id=829009897638068254)]
PROD = True

class Client(discord.Client):

    def __init__(self, *, intents: discord. Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for i in PRIORITY_GUILDS:
            self.tree.copy_global_to(guild=i)
            await self.tree.sync(guild=i)
        print("Command tree sync completed")

intents = discord.Intents.default()
client = Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="with noble feelings..."
        )
    )

@app_commands.checks.has_any_role(
    342788067297329154,  # woof
    1067984580272996422, # puppeteer
    1070448231072419850, # meister
    1067986874699874324, # esoteric engineer
    1070761008311836693  # gatekeeper
)
@client.tree.command(description="Shows the age of a BYOND account by Ckey.")
async def ckey(interaction: discord.Interaction, ckey: str):
    if PROD or interaction.guild.id == 342787099407155202:
        try:
            playerData = getPlayerData(ckey)
        except:
            await interaction.response.send_message("The Ckey you specified couldn't be found.", ephemeral=True)
            return
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{ckey}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        emb.add_field(name="Ckey", value=f"`{playerData['ckey']}`", inline=True)
        emb.add_field(name="Account Creation Date", value=f"<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:d> (<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:R>)", inline=True)
        if ccdb.status_code == 200:
            ccdbdata = ccdb.json()
            if len(ccdbdata) == 0:
                emb.add_field(name="CCDB Bans", value=f"No bans found on CCDB.", inline=True)
            else:
                activebans = 0
                totalbans = 0
                for ban in ccdbdata:
                    if ban['active']:
                        activebans += 1
                    totalbans += 1
                emb.add_field(name="CCDB Bans", value=f"{activebans} active bans and {totalbans-activebans} elapsed bans found on CCDB.", inline=True)
        embs.append(emb)
        await interaction.response.send_message(embeds=embs, ephemeral=True)
    else:
        await interaction.response.send_message("This command isn't currently available in this server - check back later!", ephemeral=True)

@client.tree.command(description="Displays a list of commands and how to use the bot.")
async def help(interaction:discord.Interaction):
    if PROD or interaction.guild.id == 342787099407155202:
        await interaction.response.send_message(f"**Commands:**\n"
                                                f"`/help` shows this message.\n"
                                                f"`/ckey` looks up a BYOND account's age by Ckey. Staff only.\n"
                                                f"\n"
                                                f"**FAQ:**\n"
                                                f"\n"
                                                f"Q: *Who should I direct technical questions to?*\n"
                                                f"A: <@188796089380503555>.\n"
                                                f"\n"
                                                f"Q: *How can I help pay for the upkeep of the bot?*\n"
                                                f"A: https://github.com/sponsors/hermaplusplus",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("This command isn't currently available in this server - check back later!", ephemeral=True)

@client.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
    else:
        #await interaction.response.send_message("⚠ An unknown error occurred! If this continues to happen, please contact <@188796089380503555>.", ephemeral=True)
        raise error

client.run(SETTINGS['TOKEN'])
#print(SETTINGS['TOKEN'])
