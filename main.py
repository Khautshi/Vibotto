import os
import discord
from typing import Union
from datetime import datetime as dt
from tracktools import UserTracker, ServerTracker
from discord.ext import commands, tasks
from discord import app_commands

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TEST_CHANNEL = 1226015133298593923
TEST_ROLE = ServerTracker().active_role
ADMIN_ROLE = "Admin"

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@tasks.loop(hours=24)
async def loop_test():
    channel = bot.get_channel(TEST_CHANNEL)
    ServerTracker().activity_scan()
    await channel.send(f"Loop test, this runs every X time. `{dt.now()}`\nCurrent loop: {loop_test.current_loop}")


@bot.event
async def on_ready():
    await loop_test.start()
    await bot.tree.sync()


@bot.event
async def on_message(message: discord.Message):
    user = message.author
    role = discord.utils.get(user.guild.roles, name=TEST_ROLE)
    if not user.bot:
        tracker = UserTracker(user.id)
        tracker.log_message()
        if role not in user.roles and tracker.is_active():
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
                       activity="Minimum amount of days a user must be active.",
                       inactivity="Maximum amount of days a user can be inactive.",
                       role="Active user role.")
@app_commands.checks.has_role(ADMIN_ROLE)
async def update_parameters(interaction, daily: int = None, activity: int = None, inactivity: int = None
                            , role: discord.Role = None):
    """Updates activity tracking parameters."""
    ServerTracker().set_params(daily=daily, activity=activity, inactivity=inactivity, role=role.name)
    await interaction.response.send_message(f"Parameters updated successfully.")


@bot.tree.command()
@app_commands.describe(user="Search target.")
@app_commands.checks.has_role(ADMIN_ROLE)
async def check_activity(interaction, user: discord.Member):
    """Displays the stored data for a given user."""
    tracker = UserTracker(user.id)
    content = tracker.get_activity()
    if content:
        await interaction.response.send_message(f"**{user.name}**```{content}```")
    else:
        await interaction.response.send_message(f"No results found for `{user.name}`")


@bot.tree.command()
@app_commands.checks.has_role(ADMIN_ROLE)
async def check_parameters(interaction):
    """Displays the current activity tracking parameters."""
    content = ServerTracker().get_params()
    if content:
        await interaction.response.send_message(f"**Parameters**```{content}```")


@bot.tree.command()
@app_commands.checks.has_role(ADMIN_ROLE)
async def force_update(interaction):
    """Test command for debugging. This will be replaced with a daily loop."""
    inactive_users = [interaction.guild.get_member(user_id) for user_id in ServerTracker().activity_scan()]
    role = discord.utils.get(interaction.guild.roles, name=TEST_ROLE)
    for user in inactive_users:
        await user.remove_roles(role)

bot.run(BOT_TOKEN)
