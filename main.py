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

import random

SETTINGS = json.load(open("settings.json", "r"))

from byond2json import player2dict as getPlayerData

#PRIORITY_GUILDS = [discord.Object(id=342787099407155202), discord.Object(id=1382867109008248832)]
PRIORITY_GUILDS = [discord.Object(id=1382867109008248832)]
VERIFICATION_CHANNEL_ID = 1431401281599311882
VERIFICATION_CHANNEL = discord.Object(id=VERIFICATION_CHANNEL_ID)
VERIFICATION_QUEUE_ID = 1431406355708772472
VERIFICATION_QUEUE = discord.Object(id=VERIFICATION_QUEUE_ID)
HIGH_STAFF_REFER = "Senior Admins"
HIGH_STAFF_ROLE_ID = 1382868045914964058
OTHER_APPROVER_REFER = "Admins"
OTHER_APPROVER_ROLE_ID = 1382867897348784158
APPROVED_ROLE_ID = 1382867109008248833
REJECT_ROLE_ID = -1
REPORTS_CHANNEL_ID = -1
UPTIME_PING_ROLE_ID = -1
DEV_PING_ROLE_ID = -1
EVENT_PING_ROLE_ID = -1
WAR_PING_ROLE_ID = -1
CODEBASE_PING_ROLE_ID = 1437852822879342853
UPDATE_PING_ROLE_ID = 1437851843526004786
PLAYTEST_PING_ROLE_ID = 1437851899494924378
RESTART_CHANNEL_ID = 1431406355708772472
GALLOWS_CHANNEL_ID = -1
MOD_LOG_ID = 1226684939844452422
DCAR_ID = 1303150042512752731

MGMT_ROLE_ID = 1382867951061045378
HOST_SPPT_ROLE_ID = 1424149066899787887

PROD = True

HELP_MESSAGE = """
**Commands:**
`/help` shows this message.
`/register` begins the registration process.

**FAQ:**

Q: *Who should I direct technical questions to?*
A: <@188796089380503555>.

Q: *How can I help pay for the upkeep of the bot?*
A: https://sponsor.herma.moe/
"""

STAFF_HELP_MESSAGE = """
**Commands:**
`/help` shows this message.
`/register` begins the registration process.

**Staff Commands:**
`/lookup` shows some details of BYOND account by Ckey and its associated Discord user.
`/ccdb` lists CCDB bans for a BYOND account by Ckey.

**FAQ:**

Q: *Who should I direct technical questions to?*
A: <@188796089380503555>.

Q: *How can I help pay for the upkeep of the bot?*
A: https://sponsor.herma.moe/
"""

class Client(discord.Client):

    def __init__(self, *, intents: discord. Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for i in PRIORITY_GUILDS:
            self.tree.copy_global_to(guild=i)
            await self.tree.sync(guild=i)
        print("Command tree sync completed")

#intents = discord.Intents.default()
#intents.members = True
#intents.guilds = True
#intents.messages = True
#intents.all = True
intents = discord.Intents.all()
client = Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="In the Palace"
        )
    )
    await client.get_channel(RESTART_CHANNEL_ID).send(":arrows_counterclockwise: **Bot restarted!** Any unprocessed registrations have been orphaned. Instruct applicants to reapply. Contact <@188796089380503555> for the manual approval process.", silent=True)

@app_commands.checks.has_any_role(
    342788067297329154,  # woof
    HIGH_STAFF_ROLE_ID,
    OTHER_APPROVER_ROLE_ID,
    MGMT_ROLE_ID,
    HOST_SPPT_ROLE_ID
)
@app_commands.describe(ckey="BYOND Username")
@app_commands.describe(discorduser="Discord User")
@app_commands.describe(public="If enabled, the output will be visible to all users.")
@client.tree.command(description="Shows some details of BYOND account by Ckey and its associated Discord user.")
async def lookup(interaction: discord.Interaction, ckey: Optional[str], discorduser: Optional[discord.User], public: Optional[bool] = False):
    await interaction.response.defer(ephemeral=True if not public else False)
    if PROD or interaction.guild.id == 342787099407155202:
        if ckey is None and discorduser is None:
            await interaction.followup.send("You must specify a Ckey or Discord user.", ephemeral=True)
            return
        if ckey is not None and discorduser is not None:
            await interaction.followup.send("You must specify only a Ckey or Discord user, not both.", ephemeral=True)
            return
        if ckey is not None:
            try:
                playerData = getPlayerData(ckey)
            except:
                await interaction.followup.send("The Ckey you specified couldn't be found.", ephemeral=True)
                return
            with open('accountlinks.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if ''.join(ch for ch in row[1] if ch.isalnum()).lower() == ''.join(ch for ch in ckey if ch.isalnum()).lower():
                        discorduser = await client.fetch_user(int(row[0]))
                        break
        if discorduser is not None:
            with open('accountlinks.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == str(discorduser.id):
                        ckey = row[1]
                        break
            try:
                playerData = getPlayerData(ckey)
            except:
                await interaction.followup.send(f"The ckey associated with {discorduser.mention} could not be found!\n## Please contact <@188796089380503555> about this immediately!", ephemeral=True)
                return
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{ckey}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        if discorduser is not None:
            emb.add_field(name="Associated Discord", value=f"{discorduser.mention}", inline=True)
            emb.add_field(name="Discord Created", value=f"<t:{int((discorduser.created_at).timestamp())}:d> (<t:{int((discorduser.created_at).timestamp())}:R>)", inline=True)
            emb.add_field(name="\u200B", value="\u200B")
        else:
            emb.add_field(name="Associated Discord", value=f"Not registered!", inline=False)
        if ckey is not None:
            emb.add_field(name="Ckey", value=f"`{playerData['ckey']}`", inline=True)
            emb.add_field(name="Account Creation Date", value=f"<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:d> (<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:R>)", inline=True)
        else:
            emb.add_field(name="Ckey", value=f"Not registered!", inline=False)
        if ckey is not None:
            emb.add_field(name="\u200B", value="\u200B")
        if ccdb.status_code == 200 and ckey is not None:
            #emb.add_field(name="\u200B", value="\u200B")
            ccdbdata = ccdb.json()
            if len(ccdbdata) == 0:
                emb.add_field(name="CCDB Bans", value=f"No bans found on CCDB.", inline=False)
            else:
                activebans = 0
                totalbans = 0
                for ban in ccdbdata:
                    if ban['active']:
                        activebans += 1
                    totalbans += 1
                emb.add_field(name="CCDB Bans", value=f"[{activebans} active, {totalbans-activebans} expired bans found on CCDB.](https://centcom.melonmesa.com/viewer/view/{ckey.replace(' ', '%20')})", inline=False)
        embs.append(emb)
        await interaction.followup.send(embeds=embs, ephemeral=True if not public else False)
    else:
        await interaction.followup.send("This command isn't currently available in this server - check back later!", ephemeral=True)

@app_commands.checks.has_any_role(
    342788067297329154,  # woof
    HIGH_STAFF_ROLE_ID,
    OTHER_APPROVER_ROLE_ID,
    MGMT_ROLE_ID,
    HOST_SPPT_ROLE_ID
)
@app_commands.describe(ckey="BYOND Username")
@app_commands.describe(page="Page Number")
@app_commands.describe(public="If enabled, the output will be visible to all users.")
@client.tree.command(description="Lists CCDB bans for a BYOND account by Ckey. Pagination begins at 1. Times displayed are in UTC.")
async def ccdb(interaction: discord.Interaction, ckey: str, page: Optional[int] = 1, public: Optional[bool] = False):
    await interaction.response.defer(ephemeral=True if not public else False)
    if PROD or interaction.guild.id == 342787099407155202:
        try:
            playerData = getPlayerData(ckey)
        except:
            await interaction.followup.send("The Ckey you specified couldn't be found.", ephemeral=True)
            return
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{ckey}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        if ccdb.status_code == 200:
            ccdbdata = ccdb.json()
            for ban in ccdbdata:
                banstatus = "Active" if ban['active'] else "Expired"
                if "unbannedBy" in ban.keys():
                    banstatus = "Unbanned"
                emb = discord.Embed(title=f"{ban['type']} Ban | {ban['sourceName']} | {banstatus}", description=f"{ban['reason']}", colour=(discord.Colour.from_rgb(108, 186, 67) if banstatus == "Active" else (discord.Colour.from_rgb(213, 167, 70) if banstatus == "Expired" else discord.Colour.from_rgb(84, 151, 224))))
                emb.add_field(name="Banned", value=f"{ban['bannedOn'].replace('T',' ').replace('Z','')}", inline=True)
                emb.add_field(name="Admin", value=f"{ban['bannedBy']}", inline=True)
                if "expires" in ban.keys():
                    emb.add_field(name="Expires", value=f"{ban['expires'].replace('T',' ').replace('Z','')}", inline=True)
                if "banID" in ban.keys():
                    emb.add_field(name="Original Ban ID", value=f"`{ban['banID']}`", inline=True)
                if "unbannedBy" in ban.keys():
                    emb.add_field(name="Unbanned By", value=f"{ban['unbannedBy']}", inline=True)
                embs.append(emb)
        if len(embs) == 0:
            await interaction.followup.send(f"No bans found on CCDB for **`{ckey}`**.", embeds=embs, ephemeral=True if not public else False)
        if len(embs) > 0 and len(embs) <= 10:
            await interaction.followup.send(f"{len(embs)} bans found on CCDB for **`{ckey}`**.", embeds=embs, ephemeral=True if not public else False)
        if len(embs) > 10:
            maxpages = math.ceil(len(embs)/10)
            await interaction.followup.send(f"{len(embs)} bans found on CCDB for **`{ckey}`**. Displaying page {min(page, maxpages)} of {maxpages}", embeds=(embs[(page-1)*10:page*10] if page <= maxpages else embs[(maxpages-1)*10:maxpages*10]), ephemeral=True if not public else False)
    else:
        await interaction.followup.send("This command isn't currently available in this server - check back later!", ephemeral=True)

#@app_commands.checks.has_any_role(
#    342788067297329154,  # woof
#    1285058932473331733, # council
#    1224452065502429206, # mod
#    1231424937315536896, # jr mod
#    1228769833261207673, # coder
#    1284667472863301673, # sprite maint
#    1278651588864512000, # wiki lead
#    1229527478893154374, # staff spriter
#    1228408987125288960, # wiki writer
#)
#@app_commands.describe(discorduser="Discord User")
#@app_commands.describe(reason="Reason for restriction")
#@client.tree.command(description="Restrict a user's access to development channels.")
#async def dcar(interaction: discord.Interaction, discorduser: discord.User, reason: str):
#    await interaction.response.defer(ephemeral=True)
#    if PROD or interaction.guild.id == 342787099407155202:
#        if DCAR_ID in [r.id for r in discorduser.roles]:
#            await interaction.followup.send(f"{discorduser.mention}'s access has already been restricted.", ephemeral=True)
#        else:
#            await discorduser.add_roles(discord.Object(DCAR_ID))
#            await interaction.followup.send(f"{discorduser.mention}'s access to public development channels has been restricted.", ephemeral=True)
#            await client.get_channel(MOD_LOG_ID).send(f"**Developer Channel Access Restriction**\nActioning user: {interaction.user.mention}\nActioned user: {discorduser.mention}\nAction taken: Added DCAR role.\nReason:\n>>> {reason}")
#    else:
#        await interaction.followup.send("This command isn't currently available in this server - check back later!", ephemeral=True)

@client.tree.command(description="Displays a list of commands and how to use the bot.")
async def help(interaction:discord.Interaction):
    if PROD or interaction.guild.id == 342787099407155202:
        if 1224447318342897664 in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message(STAFF_HELP_MESSAGE, ephemeral=True)
        else:
            await interaction.response.send_message(HELP_MESSAGE, ephemeral=True)
    else:
        await interaction.response.send_message("This command isn't currently available in this server - check back later!", ephemeral=True)

class Reg(ui.Modal, title="Registration"):
    ckey     = ui.TextInput(label="What is your Ckey (BYOND username)?",
                            style=discord.TextStyle.short,
                            placeholder="",
                            max_length=100)
    dob      = ui.TextInput(label="What is your date of birth? (YYYY-MM-DD)",
                            style=discord.TextStyle.short,
                            placeholder="YYYY-MM-DD",
                            max_length=10)
    origin   = ui.TextInput(label="Who were you invited by?",
                            style=discord.TextStyle.long,
                            placeholder="Specify the person who invited you, or where you found an invite.",
                            max_length=1000)
    history  = ui.TextInput(label="What servers have you played on previously?",
                            style=discord.TextStyle.long,
                            placeholder="",
                            max_length=1000)
    extras   = ui.TextInput(label="Additional questions:",
                            style=discord.TextStyle.long,
                            placeholder="Please enter your answers to the additional questions here.",
                            max_length=1000)

    async def on_submit(self, interaction:discord.Interaction):
        try:
            playerData = getPlayerData(self.ckey.value)
        except:
            await interaction.response.send_message("The Ckey you specified couldn't be found.", ephemeral=True)
            return
        await interaction.response.send_message("Your registration has been submitted. Please await staff approval.", ephemeral=True)
        ccdb = requests.get(f"https://centcom.melonmesa.com/ban/search/{self.ckey.value}")
        embs = []
        #emb = discord.Embed(title=playerData['key'])
        emb = discord.Embed()
        emb.add_field(name="Discord", value=f"{interaction.user.mention}", inline=True)
        emb.add_field(name="Ckey", value=f"`{playerData['ckey']}`", inline=True)
        emb.add_field(name="What is your date of birth? (YYYY-MM-DD)", value=f"Date 18 years ago: **{datetime.now().year-18:04}-{datetime.now().month:02}-{datetime.now().day:02}**\n```{self.dob.value}```", inline=False)
        emb.add_field(name="Who were you invited by?", value=f"```{self.origin.value}```", inline=False)
        emb.add_field(name="What servers have you played on previously?", value=f"```{self.history.value}```", inline=False)
        emb.add_field(name="Enter your answers to the additional questions here.", value=f"```{self.extras.value}```", inline=False)
        #emb.add_field(name='\u200b', value='``` ```')
        emb.add_field(name="Ckey Created", value=f"<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:d> (<t:{str(int(time.mktime(datetime.strptime(playerData['joined'], '%Y-%m-%d').timetuple())))}:R>)", inline=True)
        emb.add_field(name="Discord Created", value=f"<t:{int((interaction.user.created_at).timestamp())}:d> (<t:{int((interaction.user.created_at).timestamp())}:R>)", inline=True)
        if ccdb.status_code == 200:
            ccdbdata = ccdb.json()
            if len(ccdbdata) == 0:
                emb.add_field(name="CCDB Bans", value=f"No bans found on CCDB.", inline=False)
            else:
                activebans = 0
                totalbans = 0
                for ban in ccdbdata:
                    if ban['active']:
                        activebans += 1
                    totalbans += 1
                emb.add_field(name="CCDB Bans", value=f"[{activebans} active, {totalbans-activebans} expired bans found on CCDB.](https://centcom.melonmesa.com/viewer/view/{self.ckey.value.replace(' ', '%20')})", inline=False)
        #emb.set_footer(text=f"Date 18 years ago: <t:{int((datetime.now() - timedelta(days=18*365.24)).timestamp())}:d>")
        await client.get_channel(VERIFICATION_QUEUE_ID).send(embed=emb, view=Verification(interaction.user.id, self.ckey.value, self.dob.value, self.origin.value, self.history.value, self.extras.value))

class Verification(ui.View):
    def __init__(self, uid, ckey, origin, experience, interest, agreement):
        super().__init__(timeout=None)
        self.uid = uid
        self.ckey = ckey
        self.origin = origin
        self.experience = experience
        self.interest = interest
        self.agreement = agreement
    
    @ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id=f"accept")
    async def accept_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if not ( (HIGH_STAFF_ROLE_ID in [r.id for r in interaction.user.roles]) or (OTHER_APPROVER_ROLE_ID in [r.id for r in interaction.user.roles]) ):
            await interaction.followup.send(f"Only {HIGH_STAFF_REFER} and {OTHER_APPROVER_REFER} can approve registrations.", ephemeral=True)
            return
        u = interaction.guild.get_member(self.uid)
        await u.add_roles(discord.Object(APPROVED_ROLE_ID))
        buttons = [b for b in self.children]
        buttons[0].disabled = True
        buttons[0].label = "Accepted"
        self.remove_item(buttons[1])
        await interaction.followup.edit_message(interaction.message.id, view=self)
        os.system(f"echo {self.uid},{self.ckey} >> accountlinks.csv")
        try:
            await u.send(f"✅ Your application for access to **Shifting Roses** has been approved.")
            await interaction.followup.send(f"✅ <@{self.uid}>'s registration approved by {interaction.user.mention}.")
        except:
            await interaction.followup.send(f"✅ <@{self.uid}>'s registration approved by {interaction.user.mention}.\n⚠️ Failed to DM <@{self.uid}> regarding their approval.")
        self.stop()

    @ui.button(label="Reject", style=discord.ButtonStyle.red, custom_id=f"reject")
    async def reject_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if not ( (HIGH_STAFF_ROLE_ID in [r.id for r in interaction.user.roles]) or (OTHER_APPROVER_ROLE_ID in [r.id for r in interaction.user.roles]) ):
            await interaction.followup.send(f"Only {HIGH_STAFF_REFER} and {OTHER_APPROVER_REFER} can reject registrations.", ephemeral=True)
            return
        u = interaction.guild.get_member(self.uid)
        #await u.add_roles(discord.Object(REJECT_ROLE_ID))
        buttons = [b for b in self.children]
        buttons[1].disabled = True
        buttons[1].label = "Rejected"
        self.remove_item(buttons[0])
        await interaction.followup.edit_message(interaction.message.id, view=self)
        try:
            await u.send(f"⛔ Your application for access to **Shifting Roses** has been rejected. Re-apply at a later time.")
            await interaction.followup.send(f"⛔ <@{self.uid}>'s registration rejected by {interaction.user.mention}.")        
        except:
            await interaction.followup.send(f"⛔ <@{self.uid}>'s registration rejected by {interaction.user.mention}.\n⚠️ Failed to DM <@{self.uid}> regarding their rejection.")
        #if (1169202970768982076 in [r.id for r in interaction.user.roles]):
        #    await u.remove_roles(discord.Object(1169202970768982076))
        #u = interaction.guild.get_member(self.uid)
        #await u.add_roles(discord.Object(APPROVED_ROLE_ID))
        self.stop()

#class Rep(ui.Modal, title="Report"):
#    ckey = ui.TextInput(label="What is the player's Ckey (if known)?",
#                        style=discord.TextStyle.short,
#                        placeholder="",
#                        max_length=100,
#                        required=False)
#    char = ui.TextInput(label="What is the character's name (if known)?",
#                        style=discord.TextStyle.short,
#                        placeholder="",
#                        max_length=100,
#                        required=False)
#    disc = ui.TextInput(label="What is the player's Discord (if known)?",
#                        style=discord.TextStyle.short,
#                        placeholder="",
#                        max_length=100,
#                        required=False)
#    ridt = ui.TextInput(label="What is the round ID and/or time? (if known)",
#                        style=discord.TextStyle.short,
#                        placeholder="",
#                        max_length=200,
#                        required=False)
#    rson = ui.TextInput(label="What is the reason for the report?",
#                        style=discord.TextStyle.long,
#                        placeholder="Please be as detailed as possible. Use filehosts (NOT DISCORD!) for logs, screenshots, videos, etc.",
#                        max_length=1000)
#
#    async def on_submit(self, interaction:discord.Interaction):
#        reporterckey = "Unknown Ckey!"
#        with open('accountlinks.csv', 'r') as file:
#            reader = csv.reader(file)
#            for row in reader:
#                if row[0] == str(interaction.user.id):
#                    reporterckey = f"`{row[1]}`"
#        embs = []
#        emb = discord.Embed()
#        emb.add_field(name="Reporter's Discord", value=f"{interaction.user.mention}", inline=True)
#        emb.add_field(name="Reporter's Ckey", value=f"{reporterckey}", inline=True)
#        emb.add_field(name="What is the player's Ckey (if known)?", value=(f"```{self.ckey.value}```" if self.ckey.value != "" else "No response."), inline=False)
#        emb.add_field(name="What is the character's name (if known)?", value=(f"```{self.char.value}```" if self.char.value != "" else "No response."), inline=False)
#        emb.add_field(name="What is the player's Discord (if known)?", value=(f"```{self.disc.value}```" if self.disc.value != "" else "No response."), inline=False)
#        emb.add_field(name="What is the round ID and/or time?", value=(f"```{self.ridt.value}```" if self.ridt.value != "" else "No response."), inline=False)
#        emb.add_field(name="What is the reason for the report?", value=f"```{self.rson.value}```", inline=False)
#        #emb.add_field(name='\u200b', value='``` ```')
#        await client.get_channel(REPORTS_CHANNEL_ID).send(embed=emb)
#        await interaction.response.send_message("Your report has been successfully submitted.", ephemeral=True)

@client.tree.command(description="Fill out the registration form. This will be reviewed by staff.")
async def register(interaction: discord.Interaction):
    if APPROVED_ROLE_ID in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message("Approved members cannot use this command.", ephemeral=True)
        return
    if interaction.channel.id not in [381573551200796672, VERIFICATION_CHANNEL_ID]:
        await interaction.response.send_message(f"This command can only be used in <#{VERIFICATION_CHANNEL_ID}>.", ephemeral=True)
        return
    await interaction.response.send_modal(Reg())

#@client.tree.command(description="Submit a player report.")
#async def report(interaction: discord.Interaction):
#    if APPROVED_ROLE_ID not in [r.id for r in interaction.user.roles]:
#        await interaction.response.send_message("Unapproved members cannot use this command.", ephemeral=True)
#        return
#    await interaction.response.send_modal(Rep())

#@client.tree.command(description="Generates a list of approved Ckeys.")
#async def playerdata(interaction:discord.Interaction):
#    if PROD or interaction.guild.id == 342787099407155202:
#        if not ( (HIGH_STAFF_ROLE_ID in [r.id for r in interaction.user.roles]) or (OTHER_APPROVER_ROLE_ID in [r.id for r in interaction.user.roles]) ):
#            await interaction.followup.send(f"Only {HIGH_STAFF_REFER} and {OTHER_APPROVER_REFER} can generate Ckey lists.", ephemeral=True)
#            return
#        os.system("csvtool format '%(2)\\n' accountlinks.csv > playerdata.txt")
#        await interaction.response.send_message(content=f"Generated <t:{int((datetime.now()).timestamp())}:f>.", file=discord.File(open("playerdata.txt", 'rb'), filename="playerdata.txt"), ephemeral=True)

"""
@client.tree.command(description="Toggle the server uptime ping role.")
async def toggleping(interaction:discord.Interaction):
    if UPTIME_PING_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.user.add_roles(discord.Object(UPTIME_PING_ROLE_ID))
        await interaction.response.send_message("You will be pinged for server uptime announcements! 🎺", ephemeral=True)
    else:
        await interaction.user.remove_roles(discord.Object(UPTIME_PING_ROLE_ID))
        await interaction.response.send_message("You will no longer be pinged for server uptime announcements. 💤", ephemeral=True)

@client.tree.command(description="Toggle the content update ping role.")
async def toggledevping(interaction:discord.Interaction):
    if DEV_PING_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.user.add_roles(discord.Object(DEV_PING_ROLE_ID))
        await interaction.response.send_message("You will be pinged for content update announcements! 🎺", ephemeral=True)
    else:
        await interaction.user.remove_roles(discord.Object(DEV_PING_ROLE_ID))
        await interaction.response.send_message("You will no longer be pinged for content update announcements. 💤", ephemeral=True)
"""

@client.tree.command(description="Toggle an optional role.")
@app_commands.choices(role=[
    app_commands.Choice(name='codebase ping', value=0),
    app_commands.Choice(name='update ping', value=1),
    app_commands.Choice(name='playtest ping', value=2)
])
async def toggleping(interaction:discord.Interaction, role: int):
    role_id = [CODEBASE_PING_ROLE_ID, UPDATE_PING_ROLE_ID, PLAYTEST_PING_ROLE_ID][role]
    role_name = ["codebase", "update", "playtest"][role]
    if role_id not in [r.id for r in interaction.user.roles]:
        await interaction.user.add_roles(discord.Object(role_id))
        await interaction.response.send_message(f"You will be pinged for {role_name} announcements! 🎺", ephemeral=True)
    else:
        await interaction.user.remove_roles(discord.Object(role_id))
        await interaction.response.send_message(f"You will no longer be pinged for {role_name} announcements. 💤", ephemeral=True)

@client.event
async def on_message(message):
    #if message.channel.id == 1237644625783554171:
    #    if "byond://play.stonekeep.xyz:1337" in message.content:
    #        await message.channel.send(file=discord.File(f"images/{random.randint(0, 28)}.png"))
    if message.author == client.user:
        return
    if message.channel.id == VERIFICATION_CHANNEL_ID:
        if HIGH_STAFF_ROLE_ID in [r.id for r in message.author.roles] or OTHER_APPROVER_ROLE_ID in [r.id for r in message.author.roles]:
            return
        await message.delete()
    #if message.channel.id == GALLOWS_CHANNEL_ID:
    #    if HIGH_STAFF_ROLE_ID in [r.id for r in message.author.roles] or OTHER_APPROVER_ROLE_ID in [r.id for r in message.author.roles]:
    #        return
    #    await message.delete(delay=900)
    #await message.add_reaction("🗑️")

@client.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
    else:
        #await interaction.response.send_message("⚠ An unknown error occurred! If this continues to happen, please contact <@188796089380503555>.", ephemeral=True)
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="Outside the Palace"
            )
        )
        raise error

client.run(SETTINGS['TOKEN'])
#print(SETTINGS['TOKEN'])
