from discord.ext import commands
from discord import Member
import discord
import os
import random

TOKEN = os.environ.get('DOOTDOOT_TOKEN')

info = {"max_players": 4,
        "random": False}

players = {"players": [235088799074484224, 690386474012639323, 714940599798726676],#, 444, 555, 666, 777, 888, 999, 123123123, 178178178178],
        "players_rem": [],
        "captains": [],
        "team1": [],
        "team2": []}

maps = {"pick": ["one", "two", "three"],
        "ban": []}

bot = commands.Bot(command_prefix="=")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="j")
async def join(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    
    if ctx.author.id not in players["players"]:
        players["players"].append(ctx.author.id)

    #   prints players in queue while its not full
    if len(players["players"]) != info["max_players"]:
        embed = discord.Embed(
            title=f"In queue [{len(players['players'])}/{(info['max_players'])}]", 
            #   prints out name of players joined with index
            description="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(players["players"], start=1)), 
            color=0x00FF00)
        await ctx.send(embed=embed)

    #   splist group of max_players into two, then prints out the two groups
    if len(players["players"]) >= info["max_players"]:
        if info["random"] == True:
            
            players["team1"] = random.sample(players["players"], int(info["max_players"]/2))
            players["team2"] = list(set(players["players"]) - set(players["team1"]))
            
            team1 = "\n".join(f"<@{player}>" for player in players["team1"])
            team2 = "\n".join(f"<@{player}>" for player in players["team2"])
            embed = discord.Embed(
            title=f"Teams", 
                description="Team 1\n" + team1 + "\nTeam 2\n" + team2, 
                color=0xFF5500)
            embed.add_field(name="Map",value=random.choice(maps['pick']), inline=False)

            await ctx.send(embed=embed)
            await ctx.send("Team 1")
            await ctx.send("\n".join(f"<@{player}>" for player in players["team1"]))
            await ctx.send("Team 2")
            await ctx.send("\n".join(f"<@{player}>" for player in players['team2']))
            
        # picks random captains
        else:
            captains = random.sample(players["players"], 2)
            players["team1"].append(captains[0])
            players["team2"].append(captains[1])
            players["captains"].clear()
            players["captains"] += captains
            players["players_rem"] = list(set(players["players"]) - set(captains))
            await ctx.send("Captains:")
            await ctx.send("\n".join(f"<@{captain}>" for captain in captains))
            embed = discord.Embed(title="Players to pick", description="\n".join(f"<@{player}>" for player in players["players_rem"]),
                colour=0xFF5500)
            await ctx.send(embed=embed)
            
#   leave queue
@bot.command(name="l")
async def leave(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if ctx.author.id in players["players"]:
        players["players"].remove(ctx.author.id)
        await ctx.send(f"Removed {ctx.author.name} from queue")
    else:
        await ctx.send(f"{ctx.author.name} not in queue")

#   remove player from queue
@bot.command(name="r")
async def remove(ctx, player: Member=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if player == None:
        await ctx.send("```usage: =r <@player name>```")
    elif player.id in players["players"]:
        players["players"].remove(player.id)
        await ctx.send(f"Removed {player.name} from queue")
    else:
        await ctx.send(f"{player.name} not in queue")

#   options for max player limit and team randomisation
@bot.command(name="o")
async def options(ctx, arg1: int=None, arg2: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if arg1 == None or arg2 == None:
        await ctx.send("```usage: =o <max # of players> <t/f(true/false) for random teams(else random leaders are picked)>```")
    else:
        info["max_players"] = arg1
        if arg2 == "t" or arg2 == "T" or arg2 == "true" or arg2 == "True":
            info["random"] = True
        elif arg2 == "f" or arg2 == "F" or arg2 == "false" or arg2 == "False":
            info["random"] = False
        embed = discord.Embed(description=f"Max players: {info['max_players']}\nRandomise teams: {info['random']}",colour=0x00FFFF)
        await ctx.send(embed=embed)

#   pick player from list by team captain
@bot.command(name="p")
async def pick(ctx, player: Member=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if player == None:
        await ctx.send("```usage: =p @player```")
    elif player.id not in players["players_rem"]:
        await ctx.send("Player not in roster")
    elif ctx.author.id not in players["captains"]:
        await ctx.send("You not a captain m8 :rage:")
    elif len(players["team1"]) == len(players["team2"]) and ctx.author.id == players["captains"][0]:
        players["team1"].append(player.id)
        players["players_rem"].remove(player.id)
        #   if only 1 players remains to be picked, place him into team automatically
        if len(players["players_rem"]) == 1:
            players["team2"].append(players["players_rem"][0])
            players["players_rem"].remove(players["players_rem"][0])
            await ctx.send(embed=pick_embed())
            #   sends ping to players
            await ctx.send("Team 1")
            await ctx.send("\n".join(f"<@{player}>" for player in players["team1"]))
            await ctx.send("Team 2")
            await ctx.send("\n".join(f"<@{player}>" for player in players['team2']))
            #   clears queue so people can start queueueueing again
            players["players"].clear()
        else:
            await ctx.send(embed=pick_embed())
    elif len(players["team1"]) != len(players["team2"]) and ctx.author.id == players["captains"][1]:
        players["team2"].append(player.id)
        players["players_rem"].remove(player.id)
        await ctx.send(embed=pick_embed())
    else:
        await ctx.send("Tis not your turn :rage:")

# returns an embed for the captain player pick command
def pick_embed():
    team1 = "\n".join(f"<@{player}>" for player in players["team1"][1:])
    team2 = "\n".join(f"<@{player}>" for player in players["team2"][1:])
    players_remaining = "\n".join(f"<@{player}>" for player in players["players_rem"])
    nl = '\n'  # f string {} doesnt support backslashes(\)
    desc = f"***Team 1***\n**Captain:** <@{players['captains'][0]}>\n{team1}\n\n\
                ***Team 2***\n**Captain:** <@{players['captains'][1]}>\n{team2}\n\n\
                {f'**Remaining:**{nl}{players_remaining}' if players['players_rem'] else ''}"
    embed = discord.Embed(title="Teams",
        description=desc,
        colour=0xFF5500)
    if len(players["team1"]) + len(players["team2"]) == info["max_players"]:
        embed.add_field(name="Map", value=random.choice(maps['pick']), inline=False)
    return embed
    
@bot.command(name="queue")
async def queue(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if not players["players"]:
        desc = r"\**crickets*\*"
    else:
        desc ="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(players["players"], start=1))
    embed = discord.Embed(title=f"In queue [{len(players['players'])}/{(info['max_players'])}]", 
            description=desc,
            colour=0x00FF00)
    await ctx.send(embed=embed)

#   list all names
@bot.command(name="maps")
async def map_list(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    embed = discord.Embed(title="Maps",
        description="\n".join(f"[{i}] {map_string}" for i, map_string in enumerate(maps['pick'], start=1)),
        colour=0x0055FF)
    await ctx.send(embed=embed)

#   select random map
@bot.command(name="m")
async def map_random(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.send(f"map: {random.choice(maps['pick'])}")

#   add map to roster
@bot.command(name="madd")
async def map_add(ctx, map_str: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if map_str == None:
        await ctx.send("```usage: =madd <map_name>```")
    else:
        maps["pick"].append(map_str)
        await ctx.send(f"map added: {map_str}")

#   remove map from roster
@bot.command(name="mremove")
async def map_remove(ctx, map_int: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if map_int == None:
        await ctx.send("```usage: =mremove <map_number>```")
    elif len(maps["pick"]) < map_int - 1:
        await ctx.send("""```diff\n- map number out of range```""")
    else:
        await ctx.send(f"map removed: {maps['pick'][map_int - 1]}")
        del maps["pick"][map_int - 1]

@bot.command(name="whoami")
async def whoami(ctx):
    await ctx.send(f"<@{ctx.author.name}\n{ctx.author.id}\n{ctx.author}>")

@bot.command(name="members")
async def members(ctx):
    print("\n".join(f"{str(member.id)} {member.name}" for member in ctx.guild.members))

@bot.command(name="nick")
async def nick(ctx, arg1):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.author.edit(nick=arg1)

@bot.command(name="clear")
async def clear_queue(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    players["players"] = []
    await ctx.send("queue cleared")

@bot.command(name="q")
async def quit(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.bot.close()

@bot.command(name="debug")
async def debug(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    print(players)


bot.run(TOKEN)

#TODO allocate points to winning team - (change nic of players [0]Edy -> [10]Edy)
# ^ + clear team & captain lists after point allocation
#TODO add admin only restrictions to certain functions (eg. player remove, clear queue)
#TODO option to change pick order 1-2..2-1/1-1..1-1
#TODO convert to class?
#TODO save changes to file/db