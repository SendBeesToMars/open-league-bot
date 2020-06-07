from discord.ext import commands
import discord
import os
import random

TOKEN = os.environ.get('DOOTDOOT_TOKEN')
MAX_PLAYERS = 12

info = {"max_players": 12,
        "random": True}

players = [111, 222, 333, 444, 555, 666, 777, 888, 999, 123123123, 178178178178]

bot = commands.Bot(command_prefix="=")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="j")
async def join(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    
    if ctx.author.id not in players:
        players.append(ctx.author.id)

    # TODO:check why this is throwing syntax error
    max_players = info["max_players"]
    embed = discord.Embed(
        title=f"Lobby [{len(players)}/{(max_players)}]", 
        #   prints out name of players joined with index
        description="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(players, start=1)), 
        color=0x00FF00)
    await ctx.send(embed=embed)

    #   splist group of max_players into two, then prints out the two groups
    if len(players) >= info["max_players"]:
        if info["random"] == True:
            await ctx.send("Group 1")
            group1 = random.sample(players, int(info["max_players"]/2))
            group2 = list(set(players) - set(group1))
            await ctx.send("\n".join(f"<@{player}>" for player in group1))
            await ctx.send("Group 2")
            await ctx.send("\n".join(f"<@{player}>" for player in group2))
        else:
            captains = random.sample(players, 2)
            await ctx.send("Captains:")
            await ctx.send("\n".join(f"<@{captain}>" for captain in captains))
            
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
            
        print(info)

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

# pick random captains
# pick random teams =p @name
# print people in queue =q