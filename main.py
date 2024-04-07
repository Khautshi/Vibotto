import os
import discord
from discord.ext import commands
from discord import app_commands

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TEST_CHANNEL = 1226015133298593923
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    # channel = bot.get_channel(TEST_CHANNEL)
    # await channel.send("J'aldzhinn! Unn Vibotto :3")
    await bot.tree.sync()


@bot.tree.command()
@app_commands.describe(namajnen="Namájnen ka vilti antena.")
@app_commands.checks.has_role("Admin")
async def anta(interaction, namajnen: discord.Role):
    """Anta jokjhy namájnen n'aldzhinn."""
    members = bot.get_all_members()
    for member in members:
        if not member.bot and namajnen not in member.roles:
            await member.add_roles(namajnen)
    await interaction.response.send_message("jena joo!")


bot.run(BOT_TOKEN)
