import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
import random
import os
from dotenv import load_dotenv

# https://github.com/eunwoo1104/discord-py-slash-command
# https://discordpy.readthedocs.io/en/latest/index.html

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
slash = SlashCommand(bot)


@bot.command(aliases=["start", "startgame", "play"], pass_context=True)
async def start_game(ctx):
    locations = [["Restaurant", "Barkeeper", "Gast", "Spy"],["Casino","Groupier","Kunde", "Spy"]]
    await ctx.send("Test")
    # Members assignen
    author = ctx.author
    voice_channel = author.voice.channel.id
    voice_members = author.voice.channel.members
    await ctx.send(voice_channel)
    
    member_count = len(voice_members)

    if member_count > 10:
        await ctx.send("The maximum amount of players is 10.")
    else:
        # Rollen + Locations randomizen (spy etc)
        roleset = random.choice(locations)
        location = roleset[0]
        roleset.remove(location)
        spy = random.randint(0,member_count-1)

        # Direct messages to members
        for member in voice_members:
            if voice_members.index(member) == spy:
                channel = await member.create_dm()
                await ctx.send("Sending message to channel")
                await channel.send(f"Your role is: **Spy** \nYour location is: **{location}**")
            else:
                role = random.choice(roleset)
                roleset.remove(role)
                channel = await member.create_dm()
                await ctx.send("Sending message to channel")
                await channel.send(f"Your role is: **{role}** \nYour location is: **{location}**")


bot.run(DISCORD_TOKEN)
