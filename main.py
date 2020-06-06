from discord.ext import commands
import discord
import os

TOKEN = os.environ.get('DOOTDOOT_TOKEN')

players = {}

fake_players = {
    9082734659823745: "player1",
    9082734659823741: "player2",
    9082734659823742: "player3",
    9082734659823743: "player4",
    9082734659823744: "player5",
    9082734659823746: "player6",
    9082734659823711: "player7",
    9082734659823722: "player8",
    9082734659823733: "player9",
    9082734659823784: "player10",
    9082734659823794: "player11"}

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
    if players.get(ctx.author.name) != ctx.author.id:
        players[ctx.author.id] = ctx.author.name
    else:
        players[ctx.author.id] = ctx.author.name + "(1)"
    embed = discord.Embed(
        title=f"Lobby [{len(players)}/12]", 
        #   prints out name of players joined with index
        description="\n".join(f"[{i}] " + players[player] for i, player in enumerate(players, start=1)), 
        color=0x00FF00)
    await ctx.send(embed=embed)
    if len(players) == 12:
        await ctx.send("omg the partys full :)")

@bot.command(name="q")
async def quit(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.bot.close()

@bot.command(name="nick")
async def nick(ctx, arg1):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.author.edit(nick=arg1)

bot.run(TOKEN)

# pick random captains
# pick random teams =p @name
# print people in queue