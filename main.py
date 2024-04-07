import os
import discord
from typing import Union
from tracktools import ActivityTracker
from discord.ext import commands
from discord import app_commands

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TEST_CHANNEL = 1226015133298593923
TEST_ROLE = "mick test"
ADMIN_ROLE = "Admin"
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    # channel = bot.get_channel(TEST_CHANNEL)
    # await channel.send("J'aldzhinn! Unn Vibotto :3")
    await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message):
    user = message.author
    role = discord.utils.get(user.guild.roles, name=TEST_ROLE)
    if not user.bot and role not in user.roles:
        tracker = ActivityTracker(user)
        tracker.log_msg()
        if tracker.is_active():
            await user.add_roles(role)
            await message.channel.send("Maladjéts, mikkena du joo!", mention_author=True)


@bot.tree.command()
@app_commands.describe(role="The role that will be assigned.",
                       target="Who will receive the role, it can be either a user or a role.")
@app_commands.checks.has_role(ADMIN_ROLE)
async def assign(interaction, role: discord.Role, target: Union[discord.Role, discord.Member]):
    """Gives a role to a specific user or to all users with certain role. Note: bots will be ignored."""
    if isinstance(target, discord.Role):
        for target in target.members:
            if role not in target.roles:
                await target.add_roles(role)
        await interaction.response.send_message(f"Role successfully assigned to all users with `{target.name}`.")
    elif isinstance(target, discord.Member):
        if not target.bot and role not in target.roles:
            await target.add_roles(role)
            await interaction.response.send_message(f"Role successfully assigned to `{target.name}`.")
        else:
            await interaction.response.send_message(f"The role couldn't be assigned.")


@bot.tree.command()
@app_commands.describe(daily="Minimum amount of messages a user must send for it to count as a day of activity.",
                       activity="Minimum amount of days of activity for the user to be considered active.")
@app_commands.checks.has_role(ADMIN_ROLE)
async def update_parameters(interaction, daily: int = None, activity: int = None):
    """Updates activity tracking parameters."""
    tracker = ActivityTracker()
    tracker.set_threshold(daily=daily, activity=activity)
    await interaction.response.send_message(f"Update successfull")


@bot.tree.command()
@app_commands.describe(user="Search target.")
@app_commands.checks.has_role(ADMIN_ROLE)
async def check_history(interaction, user: discord.Member):
    """Displays the stored data for a given user."""
    tracker = ActivityTracker(user)
    content = tracker.get_activity()
    if content:
        await interaction.response.send_message(f"**{user.name}**\n```{content}```")


@bot.tree.command()
@app_commands.checks.has_role(ADMIN_ROLE)
async def check_parameters(interaction):
    """Displays the current activity tracking parameters."""
    tracker = ActivityTracker()
    content = tracker.get_params()
    if content:
        await interaction.response.send_message(f"**Parameters**\n```{content}```")

bot.run(BOT_TOKEN)
