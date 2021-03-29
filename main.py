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

global_spy = None
thumbs_up = 1
thumbs_down = 1
game_running = False

@bot.event
async def on_ready():
    print("Bot ready!")

@bot.command(aliases=["start", "startgame", "play"], pass_context=True)
async def start_game(ctx, wait: typing.Optional[int] = None):
    global global_spy
    global thumbs_up
    global thumbs_down
    global game_running

    if game_running == True:
      return
    game_running = True

    locations = [
        ["Restaurant","https://i.ibb.co/0qkC1Zm/restaurant-wts.jpg","Barkeeper","Guest","Waiter","Chef","Gourmet/Tester",""],
        ["Casino","https://i.ibb.co/7r4DZzR/casino-wts.jpg","Groupier","Kunde","Escord Lady","Manager","Receptionist","Ferrari Owner who just wants to flex"],
        ["Beach","https://i.ibb.co/j645RYh/beach-wts.jpg","Thief","Icecream Seller","Tourist","Lifeguard","Surfteacher",""], 
        ["Luxury Yacht","https://i.ibb.co/3YqN28b/yacht-wts.jpg","Passanger","Captain","Cook","Cleaning Crew Member","Receptionist",""],
        ["Submarine","https://i.ibb.co/rvmhDGv/submarine-wts.jpg","Captain","Sailor","Security Guard","Weapons Manager","Cook",""],
        ["University","https://i.ibb.co/Bgj2HgH/university-wts.jpg","Tutor","Student","Librarian","Visitor","Receptionist",""]
    ]
    
    text = ""
    for location in locations:
        if locations.index(location) == len(locations)-1:
            location = location[0]
            text = text + location + "."
        else:
            location = location[0]
            text = text + location + ", "

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
    elif member_count < 4:
        await ctx.send("The minimum amount of players is 4.")
    
    # Rollen + Locations randomizen (spy etc)
    roleset = random.choice(locations)
    location = roleset[0]
    roleset.remove(location)
    image = roleset[0]
    roleset.remove(image)
    spy = random.randint(0,member_count-1)

    # Direct messages to members
    for member in voice_members:
        try:
            if voice_members.index(member) == spy:
                channel = await member.create_dm()
                global_spy = member
                embed=discord.Embed(title="Who's the Spy?", description="A new game has started! Here's your role:", color=0xffe600)
                embed.add_field(name="Location", value="Find it out", inline=True)
                embed.add_field(name="Role", value="Spy", inline=True)
                embed.add_field(name="Possible locations", value=text, inline=False)
                embed.set_footer(text="Type .guess [location] in the server channel where you started the game to guess the location.")
                await channel.send(embed=embed)
            else:
                role = random.choice(roleset)
                roleset.remove(role)
                channel = await member.create_dm()
                embed=discord.Embed(title="Who's the Spy?", description="A new game has started! Here's your role:", color=0xffe600)
                embed.set_thumbnail(url=image)
                embed.add_field(name="Location", value=location, inline=True)
                embed.add_field(name="Role", value=role, inline=True)
                embed.set_footer(text="Type .vote [user] in the server channel where you started the game to vote out the spy.")
                await channel.send(embed=embed)
        except:
            await ctx.send("The DM couldn't be sent to everyone. Check if someone blocked the bot.")
            return
        
    if wait != None:
        sleep(wait)
    else:
        sleep(10)
    
    await ctx.send(f"**The game starts now!** We're starting with: {random.choice(voice_members).mention}. Ask someone a question!")


    @bot.command()
    async def vote(ctx):
        global global_spy
        global thumbs_up
        global thumbs_down
        global game_running

        if game_running == False:
          return

        mentioned = ctx.message.mentions[0]

        voting = await ctx.send(f"{ctx.author.mention} voted for {mentioned.mention}. React to vote with 👍 or 👎.")
        await voting.add_reaction("👍")
        await voting.add_reaction("👎")

        thumbs_up = 1
        thumbs_down = 1

        voting = await ctx.channel.fetch_message(voting.id)

        @bot.event
        async def on_reaction_add(reaction, user):
            global thumbs_up
            global thumbs_down
            global game_running

            if game_running == False:
                return

            if user.id == mentioned.id:
                return
            if reaction.message.id != voting.id:
                return
            elif reaction.emoji == "👍":
                thumbs_up += 1
                print(f"thumbs_up: {thumbs_up}")
            elif reaction.emoji == "👎":
                thumbs_down += 1
                print(f"thumbs_down: {thumbs_down}")
            
            if thumbs_down >= 2:
                await ctx.send("Voting failed.")
                await voting.delete()
                thumbs_down = 1
            elif thumbs_up >= member_count:
                if mentioned.id == global_spy.id:
                    await ctx.send(f"{global_spy.mention} was the spy!\nThe Crew wins!")
                    thumbs_up = 1
                    await voting.delete()
                    game_running = False
                    return
                else:
                    await ctx.send(f"{mentioned.mention} was not the spy! The real spy was {global_spy.mention}.")
                    thumbs_up = 1
                    await voting.delete()
                    game_running = False
                    return

        thumbs_up = 1
        thumbs_down = 1
        return

    @bot.command()
    async def guess(ctx, guessed_location: str):
        global game_running
        if game_running == False:
          return

        if ctx.author == global_spy:
            if guessed_location.lower() != location.lower():
                await ctx.send(f"**{guessed_location} is not right!** The real location was {location}. The crew wins!")
                game_running = False
                return
            else:
                await ctx.send(f"**{guessed_location} is right!** The spy wins!")
                game_running = False
                return

bot.run(DISCORD_TOKEN)