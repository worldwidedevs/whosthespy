import discord
from discord.ext import commands
#from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
import random
import os
from dotenv import load_dotenv
from time import sleep
import typing
from replit import db
import logging

# https://github.com/eunwoo1104/discord-py-slash-command
# https://discordpy.readthedocs.io/en/latest/index.html

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
#slash = SlashCommand(bot)

logging.basicConfig(filename="logs/bot.log", filemode="w", format="%(asctime)s - [%(levelname)s] %(name)s : %(message)s", datefmt="%H:%M:%S")

'''
db[channel_id+".spy"] = ""
db[channel_id+".thumbsup"] = ""
db[channel_id+".thumbsdown"] = ""
db[channel_id+".gamerunning"] = True
db[channel_id+".location"] = ""
db[channel_id+".membercount"] = ""

logging.debug("This is a debug message")
logging.info("This is an info message")
logging.warning("This is a warning message")
logging.error("This is an error message")
logging.critical("This is a critical message")
'''

def delkeys(channel_id):
    try:
        del db[channel_id+".spy"]
        del db[channel_id+".thumbsup"]
        del db[channel_id+".thumbsdown"]
        del db[channel_id+".gamerunning"]
        del db[channel_id+".location"]
        del db[channel_id+".membercount"]
        return True
    except:
        return False


@bot.event
async def on_ready():
    try:
        db["startup_checksum"] = True
        if db["startup_checksum"] == True:
            del db["startup_checksum"]
            print("Database working")

            if db.keys():
                try:
                    for key in db.keys():
                        del db[key]
                    print("Deleted Database keys")
                except:
                    print("Failed to delete Database keys")
                    logging.error("Failed to delete Database keys while starting")
        else:
            del db["startup_checksum"]
            print("Database error")
            logging.error("Database error while starting")
    except:
        print("Fatal Database error")
        logging.critical("Fatal Database error while starting")
    finally:
        print("------")

    guild_count = 0
  
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    
    for guild in bot.guilds:
        print("{0} : {1}".format(guild.id, guild.name))
        guild_count = guild_count + 1
    
    await bot.change_presence(activity=discord.Game(name=f"on {guild_count} servers | .help"))
    
    print("Bot is in " + str(guild_count) + " guilds")
    print("------")
    print("Startup complete!")
    logging.info("Bot started successfully")

@bot.command(aliases=["start", "startgame", "play"], pass_context=True)
async def start_game(ctx, wait: typing.Optional[int] = None):
    channel_id = str(ctx.channel.id)

    try:
        if db[channel_id+".gamerunning"] == True:
            return
    except:
        db[channel_id+".gamerunning"] = True

    locations = [
        ["Restaurant","https://i.ibb.co/0qkC1Zm/restaurant-wts.jpg","Barkeeper","Guest","Waiter","Chef","Gourmet/Tester"],
        ["Casino","https://i.ibb.co/7r4DZzR/casino-wts.jpg","Groupier","Customer","Escord Lady","Manager","Receptionist","Ferrari Owner who just wants to flex"],
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
    db[channel_id+".membercount"] = member_count


    max_players = len(locations[0])-2
    if member_count > max_players:
        await ctx.send(f"The maximum amount of players is {max_players}.")
        return
    #elif member_count < 4:
    #    await ctx.send("The minimum amount of players is 4.")
    
    # Rollen + Locations randomizen (spy etc)
    roleset = random.choice(locations)
    location = roleset[0]
    db[channel_id+".location"] = location
    roleset.remove(location)
    image = roleset[0]
    roleset.remove(image)
    spy = random.randint(0,member_count-1)

    # Direct messages to members
    for member in voice_members:
        try:
            if voice_members.index(member) == spy:
                channel = await member.create_dm()
                embed=discord.Embed(title="Who's the Spy?", description="A new game has started! Here's your role:", color=0xffe600)
                embed.add_field(name="Location", value="Find it out", inline=True)
                embed.add_field(name="Role", value="Spy", inline=True)
                embed.add_field(name="Possible locations", value=text, inline=False)
                embed.set_footer(text="Type .guess [location] in the server channel where you started the game to guess the location.")
                await channel.send(embed=embed)
                db[channel_id+".spy"] = member
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
        except Exception as exception:
            await ctx.send("The DM couldn't be sent to everyone. Check if someone blocked the bot.")
            logging.error(f"Exception while sending DMs - {exception}")
            return
        
    if wait != None:
        sleep(wait)
    else:
        sleep(10)
    
    await ctx.send(f"**The game starts now!** We're starting with: {random.choice(voice_members).mention}. Ask someone a question!")


@bot.command()
async def vote(ctx):
    channel_id = str(ctx.channel.id)

    if db[channel_id+".gamerunning"] == False:
      return

    mentioned = ctx.message.mentions[0]

    voting = await ctx.send(f"{ctx.author.mention} voted for {mentioned.mention}. React to vote with 👍 or 👎.")
    await voting.add_reaction("👍")
    await voting.add_reaction("👎")

    db[channel_id+".thumbsup"] = 1
    db[channel_id+".thumbsdown"] = 1

    voting = await ctx.channel.fetch_message(voting.id)

    @bot.event
    async def on_reaction_add(reaction, user):
        channel_id = str(ctx.channel.id)

        if db[channel_id+".gamerunning"] == False:
            return
        spy = db[channel_id+".spy"]

        if user.id == mentioned.id:
            return
        if reaction.message.id != voting.id:
            return
        elif reaction.emoji == "👍":
            db[channel_id+".thumbsup"] += 1
        elif reaction.emoji == "👎":
            db[channel_id+".thumbsdown"] += 1
                
        if db[channel_id+".thumbsdown"] >= 2:
            await ctx.send("Voting failed.")
            await voting.delete()
            thumbs_down = 1
        elif db[channel_id+".thumbsup"] >= db[channel_id+".membercount"]:
            if mentioned.id == spy.id:
                await ctx.send(f"{spy.mention} was the spy!\nThe Crew wins!")
                thumbs_up = 1
                await voting.delete()
                delkeys(channel_id)
                return
            else:
                await ctx.send(f"{mentioned.mention} was not the spy! The real spy was {spy.mention}.")
                thumbs_up = 1
                await voting.delete()
                delkeys(channel_id)
                return

@bot.command()
async def guess(ctx, guessed_location: str):
    channel_id = str(ctx.channel.id)

    if db[channel_id+".gamerunning"] == False:
      return

    location = db[channel_id+".location"]

    if ctx.author == db[channel_id+".spy"]:
        if guessed_location.lower() != location.lwer():
            await ctx.send(f"**{guessed_location} is not right!** The real location was {location}. The crew wins!")
            delkeys(channel_id)
            return
        else:
            await ctx.send(f"**{guessed_location} is right!** The spy wins!")
            delkeys(channel_id)
            return

bot.run(DISCORD_TOKEN)