import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
import random
import os
from dotenv import load_dotenv
from time import sleep
import typing

# https://github.com/eunwoo1104/discord-py-slash-command
# https://discordpy.readthedocs.io/en/latest/index.html

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
slash = SlashCommand(bot)


@bot.command(aliases=["start", "startgame", "play"], pass_context=True)
async def start_game(ctx, wait: typing.Optional[int] = None):
    locations = [
        ["Restaurant","Barkeeper","Guest","Waiter","Chef","Gourmet"],
        ["Casino","Groupier","Kunde","Escord Lady","Manager","Receptionist"], 
        ["Strand","Thief","Icecream Seller","Tourist","Lifeguard"], 
        ["Luxury Yacht","Passanger","Captain","Cook","Cleaning Crew Member","Receptionist"],
        ["Submarine","Captain","Sailor","Security Guard","Weapons Manager","Cook"]
    ]
    
    # Members assignen
    author = ctx.author
    try:
        voice_channel = author.voice.channel.id
        voice_members = author.voice.channel.members
    except AttributeError:
        await ctx.send("You can only start a game while you're on a server, in a voice channel together with your friends.")
        return
    
    await ctx.send("Starting the game! You'll be receiving your roles via DM shortly.")
    member_count = len(voice_members)

    if member_count > 10:
        await ctx.send("The maximum amount of players is 10.")
        return
    
    # Rollen + Locations randomizen (spy etc)
    roleset = random.choice(locations)
    location = roleset[0]
    roleset.remove(location)
    spy = random.randint(0,member_count-1)

    # Direct messages to members
    for member in voice_members:
        if voice_members.index(member) == spy:
            channel = await member.create_dm()
            await channel.send("Your role is: **Spy** \nGuess the location!")
        else:
            role = random.choice(roleset)
            roleset.remove(role)
            channel = await member.create_dm()
            await channel.send(f"Your role is: **{role}** \nYour location is: **{location}**")
        
    sleep(15)
    await ctx.send(f"**The game starts now!** We're starting with: {random.choice(voice_members).mention}. Ask someone a question!")

    if wait != None:
        sleep(wait)
    else:
        sleep(10)

    
        
        



'''
@bot.commands(aliases=["thespyis"], pass_context=True)
async def guess(ctx):
    user = ctx.message.mentions[0]
    await ctx.send(f"{user.mention} wurde angeklagt. Bitte reacten.")
    # bei member_count reactions die Rolle des Angeklagten überprüfen
'''

bot.run(DISCORD_TOKEN)