import discord
from glob import glob
import requests
import time
from pprint import pprint
from aiohttp import request
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
from discord.ext.commands import has_permissions, CommandNotFound
from turtle import color
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ..db import db
spotify = "./lib/db/spotify.json"
 
# requests apscheduler discord.py required

prefix = None
admin_ids = [851473518214250507]
needed_intents = discord.Intents.all()
cmds = [path.split("\\")[-1][:-3] for path in glob(".lib/commands/*.py")]


class client(discord.Client):
    def __init__(self):
        self.prefix = prefix
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        self.synced = False
        self.added = False

        db.autosave(self.scheduler)

        super().__init__(command_prefix=prefix, intents=needed_intents,
                         help_command=None, owner_ids=admin_ids)

# error handling and uh running the bot yes

    def run(self, version):
        self.VERSION = version
        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        print("running the bot wait")
        super().run(self.TOKEN, reconnect=True)
# timed notifys

    async def event_notify(self):
        channel = self.get_channel(1036627652645228565)
        await channel.send("15 minutes have passed @everyone")

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
            # self.scheduler.add_job(self.event_notify, CronTrigger(
            #     day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()
            self.stdout = self.get_channel(1036627652645228565)

        print(f"Logged in as {self.user}")
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong. Please report this to a staff member.")
            # logs channel pak v db
            await self.stdout.send("An error occured.")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send("Sorry! This command does not exist.")
        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc


client = client()
tree = app_commands.CommandTree(client)

# HELP COMMAND


@tree.command(name="help", description="Shows a list of all available commands.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title=f'Akari moderation commands', description=None)
    embed.add_field(name=f"/ban <member> <reason>",
                    value="*Kick/ban perms only command*: Permanently bans a certain member.", inline=False)
    embed.add_field(name=f"/unban <member>",
                    value="*Kick/ban perms only command*: Unbans a certain member.", inline=False)
    embed.add_field(name=f"/kick <member> <reason>",
                    value="*Kick/Ban perms only command*: Kicks a certain member.", inline=False)
    embed.add_field(name=f"/report <member> <reason> <proof>",
                    value="*Admin only command*: Deletes a certain amount of messages.", inline=False)
    embed.add_field(name=f"/name <member> <name>",
                    value="Sets a server nickname.", inline=False)
    embed.add_field(
        name=f"/hug", value="Sends a random anime hug gif.", inline=False)
    embed.add_field(name=f"/helpspotify",
                    value="Shows a list of commands for the spotify module.", inline=False)
    embed.add_field(name=f"/help", value="Shows this message.", inline=False)
    embed.set_footer(text="with love from sky :3")
    await interaction.response.send_message(embed=embed)

# SPOTIFY HELP COMMANDS


@tree.command(name="helpspotify", description="Shows a list of all available commands.")
async def helpspotify(interaction: discord.Interaction):
    embed = discord.Embed(title=f'Akari spotify commands', description=None)
    embed.add_field(name=f"/screate",
                    value="Create a playlist on spotify.", inline=False)
    embed.add_field(
        name=f"/sadd", value="Add a song to a spotify playlist.", inline=False)
  #  embed.add_field(
  #     name=f"/sremove", value="Remove a song from a spotify playlist.", inline=False)
    # embed.add_field(
    #     name=f"/stop", value="Get your top spotify artists or tracks.", inline=False)
    # embed.add_field(name=f"/splaylists",
    #                 value="Get a list of your playlists.", inline=False)
    embed.add_field(name=f"/splaying",
                    value="Get info on a song you're currently playing.", inline=False)
    embed.add_field(name=f"/helpspotify",
                    value="Shows this message.", inline=False)
    embed.set_footer(text="with love from sky :3")
    await interaction.response.send_message(embed=embed)


# BAN COMMAND
@tree.command(name="ban", description="Bans a certain member.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, *, reason: str):
    message = (
        f'I have successfully banned {member.name}#{member.discriminator} reason: {reason}')
    embed = discord.Embed(
        title=f'You have been banned from {interaction.guild.name}',
        description=None
    )
    embed.set_author(
        name=f"Dear {member.name}#{member.discriminator},",
        icon_url="https://media.discordapp.net/attachments/1028283473099771985/1035724603026329671/Artboard_6-8.jpg?width=647&height=647"
    )
    embed.add_field(
        name=f"Banned by: ",
        value=interaction.user.mention,
        inline=True
    )
    embed.add_field(
        name=f"Reason: ",
        value=reason,
        inline=True
    )
    embed.set_footer(text="Expires in: Never")
    select = Select(options=[
        discord.SelectOption(
            label="Unban",
            emoji="⚠️",
            description="Unbans the member"
        )
    ])
    view = View()
    view.add_item(select)
    await member.send(embed=embed)
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{message}", view=view)

# BAN ERROR


@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(f'{interaction.user.mention} Sorry you cannot use this command.')


# UNBAN COMMAND
@tree.command(name="unban", description="Unbans a certain member.")
@commands.has_permissions(ban_members=True)
@commands.guild_only()
async def unban(interaction: discord.Interaction, *, member: discord.User):
    message = (
        f'I have successfully unbanned {member.name}#{member.discriminator}')

    select = Select(
        placeholder="Select an action.",
        options=[
            discord.SelectOption(
                label="Ban",
                emoji="⚠️",
                description="Bans the member again"
            ),
            discord.SelectOption(
                label="Add Member Role",
                emoji="😥",
                description="Add a member role"
            )
            # default=True
            # min_valuers user muze vybrat nejmene
        ])
    # callback ban

    async def bancallback(interaction):
        if select.values[0] == "Ban":
            await member.ban(reason=None)
        await interaction.response.send_message(f"Success.")
    select.callback = bancallback

    view = View()
    view.add_item(select)
    await interaction.guild.unban(member)
    await interaction.response.send_message(f"{message}", view=view)

# STAFF ROLE SETUP


@tree.command(name="staff", description="Setup a staff role")
@commands.guild_only()
async def staff(interaction: discord.Interaction, staffrole: discord.Role):
    message = (f'Successfully set up')
    await interaction.response.send_message(message)

# REPORT COMMAND


@tree.command(name="report", description="Report a member. (false reporting may result in a ban)")
@commands.guild_only()
# proof treba mesage link nebo pic
async def report(interaction: discord.Interaction, member: discord.Member, *, reason: str, proof: str):
    message = (f'Successfully reported {member.name}#{member.discriminator}')
    channel = interaction.guild.get_channel(1036627652645228565)
    embed = discord.Embed(
        title="<:warning:1036630452070518795> New Report <:warning:1036630452070518795>",
        description=f"{member.mention} has been reported by {interaction.user.mention}",
        timestamp=datetime.now()
    )
    embed.add_field(
        name="Reason: ",
        value=f"{reason}",
        inline=True
    )
    embed.add_field(
        name="Evidence: ",
        value=f"{proof}",
        inline=True
    )
    embed.add_field(
        name="Take an action?",
        value="Please review this report properly before taking any actions.",
        inline=False
    )

    warn = discord.Embed(
        title=f'You have been warned in {interaction.guild.name}',
        description=None
    )
    warn.set_author(
        name=f"Dear {member.name}#{member.discriminator},",
        icon_url=None
    )
    warn.add_field(
        name=f"Reason: ",
        value=f"Someone has reported you for: **{reason}**. After a proper review of this case our team has decided to give you a warning (Such behavior may result in a ban or timeout)",
        inline=False
    )
    warn.set_footer(
        text="Please read our rules."
    )

    select = Select(
        placeholder="Select an action.",
        options=[
            discord.SelectOption(
                label="Timeout",
                value="0",
                emoji="🕐",
                description="Timeout this user for a week"
            ),
            # default=True
            # min_valuers user muze vybrat nejmene
            discord.SelectOption(
                label="Ban",
                value="1",
                emoji="⛔",
                description="Permanently ban this user"
            ),
            discord.SelectOption(
                label="Warn",
                value="2",
                emoji="⚠️",
                description="Send this user a warning in DMS"
            )

        ])
# BAN OPTION CALLBACK

    async def bancalslback(interaction: discord.Interaction):
        if select.values[0] == "1":
          #  await member.send(embed=udelat treba import emvedu yk)
            await member.ban(reason=None)
            await interaction.response.send_message(f"Successfully banned this member.")
        elif select.values[0] == "2":
            await member.send(embed=warn)
        await interaction.response.send_message(f"Successfully warned this member.")
    select.callback = bancalslback

    view = View()
    view.add_item(select)
    await interaction.response.send_message(f"{message}")
    await channel.send(embed=embed, view=view)


@tree.command(name="name", description="Sets a server nickname.")
async def name(interaction: discord.Interaction, member: discord.Member, name: str):
    await interaction.response.send_message(f"Successfully changed {member.mention}\'s nickname to `{name}`")
    await member.edit(nick=name)



@tree.command(name="hug", description="Sends a random anime hug gif.")
async def hug(interaction: discord.Interaction):
    URL = "https://some-random-api.ml/animu/hug"
    async with request("GET", URL, headers={}) as response:
        if response.status == 200:
            data = await response.json()
            await interaction.response.send_message(data["link"])
        else:
            await interaction.response.send_message(f"API not available. {response.status}")



# SPOTIFY

@tree.command(name="screate", description="Create a playlist on spotify.")
async def screate(interaction: discord.Interaction, user_id: str, token: str, name: str, public: bool, collaborative: bool, description: str):
    SPOTIFY_CREATE_PLAYLIST_URL = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    ACCESS_TOKEN = f"{token}"
    response = requests.post(
        SPOTIFY_CREATE_PLAYLIST_URL,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        },
        json={
            "name": name,
            "public": public,
            "collaborative": collaborative,
            "description": description,
        }
    )
    await interaction.response.send_message("yaya")
    json_resp = response.json()
    return json_resp


@tree.command(name="sadd", description="Add a song to a spotify playlist.")
async def sadd(interaction: discord.Interaction, playlist_id: str, token: str, position: int, uris: str):
    SPOTIFY_ADD_TO_PLAYLIST_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    ACCESS_TOKEN = f"{token}"
    response = requests.post(
        SPOTIFY_ADD_TO_PLAYLIST_URL,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        },
        json={
            "position": position,
            "uris": [
                f"spotify:track:{uris}"
            ],
        }
    )
    json_resp = response.json()
    await interaction.response.send_message("Added. :)")
    return json_resp


# @tree.command(name="sremove", description="Remove a song from a spotify playlist.")
# async def sremove(interaction: discord.Interaction, playlist_id: str, token: str, uris: str):
#     SPOTIFY_DELETE_FROM_A_PLAYLIST_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
#     ACCESS_TOKEN = f"{token}"
#     response = requests.delete(
#         SPOTIFY_DELETE_FROM_A_PLAYLIST_URL,
#         headers={
#             "Authorization": f"Bearer {ACCESS_TOKEN}"
#             'Content-Type: application/json'
#         },
#         json={
#             "tracks": [
#                 f"spotify:track:{uris}"
#             ]
#         }
#     )
#     json_resp = response.json()
#     await interaction.response.send_message(json_resp)
#     return json_resp


# @tree.command(name="stop", description="Get your top spotify artists or tracks.")
# async def stop(interaction: discord.Interaction, type: str, token: str):
#     SPOTIFY_GET_A_TOP_URL = f"https://api.spotify.com/v1/me/top/{type}"
#     ACCESS_TOKEN = f"{token}"
#     response = requests.get(
#         SPOTIFY_GET_A_TOP_URL,
#         headers={
#             "Authorization": f"Bearer {ACCESS_TOKEN}"
#             'Content-Type: application/json'
#         },
#     )
#     json_resp = response.json()
#     await interaction.response.send_message(f"HULI TO FOTRA - {json_resp}")
#     print(json_resp)
#     return json_resp


# @tree.command(name="splaylists", description="Get a list of your playlists.")
# async def splaylists(interaction: discord.Interaction, user_id: str, token: str):
#     SPOTIFY_GET_PLAYLISTS_URL = f"https://api.spotify.com/v1/users/{user_id}/playlists"
#     ACCESS_TOKEN = f"{token}"
#     response = requests.get(
#         SPOTIFY_GET_PLAYLISTS_URL,
#         headers={
#             "Authorization": f"Bearer {ACCESS_TOKEN}"
#         },
#     )
#     json_resp = response.json()
#     await interaction.response.send_message(f"HULI TO FOTRA - {json_resp}")
#     return json_resp


@tree.command(name="splaying", description="Get info on a song you're currently playing.")
async def get_current_track(interaction: discord.Interaction, token: str, ):
    ACCESS_TOKEN = f"{token}"
    SPOTIFY_URL = "https://api.spotify.com/v1/me/player/"
    response = requests.get(
        SPOTIFY_URL,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
    )
    resp_json = response.json()
    track_id = resp_json["item"]["id"]
    track_name = resp_json["item"]["name"]
    artists = resp_json["item"]["artists"]
    artists_names = ", ".join([artist["name"] for artist in artists])
    link = resp_json["item"]["external_urls"]["spotify"]
    playlist = resp_json["context"]["external_urls"]["spotify"]
    preview = resp_json["item"]["preview_url"]
    volume = resp_json["device"]["volume_percent"]
    imgs = resp_json["item"]["album"]["images"][0]["url"]
    current_track_info = {
        "id": track_id,
        "name": track_name,
        "artists": artists_names,
        "link": link,
        "playlist": playlist,
        "preview": preview,
        "images": imgs
    }
    embed = discord.Embed(
        title=None,
        description=None,
    )
    embed.add_field(
        name=f"Your currently playing song is: ",
        value=track_name,
        inline=True
    )
    embed.add_field(
        name=f"By: ",
        value=artists_names,
        inline=True
    )
    embed.add_field(
        name=f"Track id: ",
        value=track_id,
        inline=True
    )
    embed.add_field(
        name=f"Link: ",
        value=link,
        inline=True
    )
    embed.add_field(
        name=f"In playlist: ",
        value=playlist,
        inline=True
    )
    embed.add_field(
        name=f"Volume percentage: ",
        value=f"{volume}%",
        inline=True
    )
    embed.set_thumbnail(url=imgs)
    embed.set_footer(text="with love from sky :3")

    playlist_id = "53SU6nqjQLoT8kHbBapn3v"
    SPOTIFY_ADD_TO_PLAYLIST_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    ACCESS_TOKEN = f"{token}"

    select = Select(
        placeholder="Select an action.",
        options=[
            discord.SelectOption(
                label="Add to a playlist.",
                value="0",
                emoji="✅",
                description="Add this song to a playlist."
            ),
            # default=True
            # min_valuers user muze vybrat nejmene
            discord.SelectOption(
                label="Like this song (available soon..)",
                value="1",
                emoji="👍",
                description="Add this song to liked songs."
            ),
        ])
# BAN OPTION CALLBACK

    async def addcallback(interaction: discord.Interaction):
        if select.values[0] == "0":
          #  await member.send(embed=udelat treba import emvedu yk)
            requests.post(
                SPOTIFY_ADD_TO_PLAYLIST_URL,
                headers={
                    "Authorization": f"Bearer {ACCESS_TOKEN}"
                },
                json={
                    "uris": [
                        f"spotify:track:{track_id}"
                    ],
                }
            )
            await interaction.response.send_message(f"Successfully added this song to a public general playlist - https://open.spotify.com/playlist/53SU6nqjQLoT8kHbBapn3v.")
        elif select.values[0] == "1":
            await interaction.response.send_message(f"Sorry, this option is currently unavailable.")
    select.callback = addcallback

    view = View()
    view.add_item(select)

    await interaction.response.send_message(embed=embed, view=view)
    pprint(current_track_info, indent=4)
    return current_track_info



