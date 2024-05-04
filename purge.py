import discord
from discord import app_commands
from discord import ui
from discord import utils

from typing import Optional

from datetime import datetime, timedelta

import time

import json
import csv

import requests

import math

import os

import subprocess

SETTINGS = json.load(open("settings.json", "r"))

from byond2json import player2dict as getPlayerData

PRIORITY_GUILDS = [discord.Object(id=342787099407155202), discord.Object(id=1169125844246069298)]
#PRIORITY_GUILDS = [discord.Object(id=342787099407155202)]
VERIFICATION_CHANNEL_ID = 1224863354590593087
VERIFICATION_CHANNEL = discord.Object(id=VERIFICATION_CHANNEL_ID)
VERIFICATION_QUEUE_ID = 1224860154864865280
VERIFICATION_QUEUE = discord.Object(id=VERIFICATION_QUEUE_ID)
HIGH_STAFF_REFER = "Wizards"
HIGH_STAFF_ROLE_ID = 1224447318342897664
OTHER_APPROVER_REFER = "Server Moderators"
OTHER_APPROVER_ROLE_ID = 1224452065502429206
APPROVED_ROLE_ID = 1224852178435571774
REJECT_ROLE_ID = 1233520171038019675
REPORTS_CHANNEL_ID = 1224860186548895916
UPTIME_PING_ROLE_ID = 1228522142526869614
RESTART_CHANNEL_ID = 1224860154864865280
GALLOWS_CHANNEL_ID = 1233520545543487609

PROD = True

class Client(discord.Client):

    def __init__(self, *, intents: discord. Intents):
        super().__init__(intents=intents)
        #self.tree = app_commands.CommandTree(self)

    #async def setup_hook(self):
    #    for i in PRIORITY_GUILDS:
    #        self.tree.copy_global_to(guild=i)
    #        await self.tree.sync(guild=i)
    #    print("Command tree sync completed")

intents = discord.Intents.all()
client = Client(intents=intents)

async def check_approval(id):
    with open('accountlinks.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(id):
                return True
    return False

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    for member in client.get_guild(1169125844246069298).members:
        if member.bot:
            continue
        if 1224852178435571774 in [r.id for r in member.roles]:
            approved = await check_approval(str(member.id))
            if not approved:
                print(f"Remove {member.display_name}")

client.run(SETTINGS['TOKEN'])
