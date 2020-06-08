from discord.ext import commands
import discord
import os
import random

TOKEN = os.environ.get('DOOTDOOT_TOKEN')
MAX_PLAYERS = 12

info = {"max_players": 12,
        "random": False}

players = {"players": [111, 222, 333, 444, 555, 666, 777, 888, 999, 123123123, 178178178178],
        "players_left": [],
        "captains": [],
        "team1": [],
        "team2": []}

bot = commands.Bot(command_prefix="=")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="j")
async def join(ctx):
    global players
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    
    if ctx.author.id not in players["players"]:
        players["players"].append(ctx.author.id)

    embed = discord.Embed(
        title=f"Lobby [{len(players['players'])}/{(info['max_players'])}]", 
        #   prints out name of players joined with index
        description="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(players["players"], start=1)), 
        color=0x00FF00)
    await ctx.send(embed=embed)

    #   splist group of max_players into two, then prints out the two groups
    if len(players["players"]) >= info["max_players"]:
        if info["random"] == True:
            await ctx.send("Team 1")
            players["team1"].append(random.sample(players["players"], int(info["max_players"]/2)))
            players["team2"].append(list(set(players["players"]) - set(players["team1"])))
            await ctx.send("\n".join(f"<@{player}>" for player in info["team1"]))
            await ctx.send("Team 2")
            await ctx.send("\n".join(f"<@{player}>" for player in players['team2']))
            
        # picks random captains
        else:
            captains = random.sample(players["players"], 2)
            players["team1"].append(captains[0])
            players["team2"].append(captains[1])
            players["captains"].clear()
            players["captains"] += captains
            players["players_left"] = list(set(players["players"]) - set(captains))
            await ctx.send("Captains:")
            await ctx.send("\n".join(f"<@{captain}>" for captain in captains))
            embed = discord.Embed(title="Players to pick", description="\n".join(f"<@{player}>" for player in players["players_left"]) ,colour=0xFF5500)
            await ctx.send(embed=embed)
            
#   options for max player limit and team randomisation
@bot.command(name="o")
async def options(ctx, arg1=None, arg2=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if arg1 == None or arg2 == None or type(arg1) == int:
        await ctx.send("```usage: =o <max # of players> <t/f(true/false) for random teams(else random leaders are picked)>```")
    else:
        info["max_players"] = int(arg1)
        if arg2 == "t" or arg2 == "T" or arg2 == "true" or arg2 == "True" :
            info["random"] = True
        elif arg2 == "f" or arg2 == "F" or arg2 == "false" or arg2 == "False":
            info["random"] = False
        embed = discord.Embed(description=f"Max players: {info['max_players']}\nRandomise teams: {info['random']}",colour=0x00FFFF)
        await ctx.send(embed=embed)

@bot.command(name="p")
async def pick(ctx, arg1=None):
    arg1 = int(arg1[3:-1])
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if arg1 == None:
        await ctx.send("```usage: =p @player```")
    elif arg1 not in players["players_left"]:
        await ctx.send("Player not in roster")
    elif ctx.author.id not in players["captains"]:
        await ctx.send("You not a captain m8 :rage:")
    elif len(players["team1"]) == len(players["team2"]) and ctx.author.id == players["captains"][0]:
        players["team1"].append(arg1)
        players["players_left"].remove(arg1)
        embed = discord.Embed(title="Players to pick", description="\n".join(f"<@{player}>" for player in players["players_left"]) ,colour=0xFF5500)
        await ctx.send(embed=embed)
    elif len(players["team1"]) != len(players["team2"]) and ctx.author.id == players["captains"][1]:
        players["team2"].append(arg1)
        players["players_left"].remove(arg1)
        embed = discord.Embed(title="Players to pick", description="\n".join(f"<@{player}>" for player in players["players_left"]) ,colour=0xFF5500)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Tis not your turn :rage:")
    

@bot.command(name="q")
async def quit(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.bot.close()

@bot.command(name="c")
async def check(ctx):
    print(ctx.author)
    await ctx.send(f"<@{ctx.author.id}>")

@bot.command(name="nick")
async def nick(ctx, arg1):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.author.edit(nick=arg1)

bot.run(TOKEN)

# print people in queue =q