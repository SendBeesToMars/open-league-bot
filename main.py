from discord.ext import commands
import discord
import os
import random

TOKEN = os.environ.get('DOOTDOOT_TOKEN')
MAX_GROUP_SIZE = 12

players = []

# fake_players = {
#     111: "player1",
#     222: "player2",
#     333: "player3",
#     444: "player4",
#     555: "player5",
#     666: "player6",
#     777: "player7",
#     888: "player8",
#     999: "player9",
#     12312312: "player10",
#     6969696969696969696: "player11"}

fake_players = [111, 222, 333, 444, 555, 666, 777, 888, 999, 123123123, 178178178178]

players = fake_players

bot = commands.Bot(command_prefix="=")



@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="j")
async def join(ctx):
    global players
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    
    if ctx.author.id not in players:
        players.append(ctx.author.id)

    embed = discord.Embed(
        title=f"Lobby [{len(players)}/{MAX_GROUP_SIZE}]", 
        #   prints out name of players joined with index
        description="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(players, start=1)), 
        color=0x00FF00)
    await ctx.send(embed=embed)

    #   splist group of MAX_GRUUP_SIZE into two, then prints out the two groups
    if len(players) >= MAX_GROUP_SIZE:
        await ctx.send("Group 1")
        randomised_players = random.sample(players, int(MAX_GROUP_SIZE/2))
        await ctx.send("\n".join(f"<@{player}>" for player in randomised_players))
        await ctx.send("Group 2")
        await ctx.send("\n".join(f"<@{player}>" for player in list(set(players) - set(randomised_players))))
        return

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