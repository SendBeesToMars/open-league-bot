from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions
import discord
import os
import random
import json
import re


TOKEN = os.environ.get('DOOTDOOT_TOKEN')

options = {"max_players": 4,
        "random": True,
        "pick_order": 1}

# info = {"players": [235088799074484224, 690386474012639323, 714940599798726676],#, 444, 555, 666, 777, 888, 999, 123123123, 178178178178],
info = {"captains": [],
        "team1": [],
        "team2": [],
        "winner": None}

queue = {"players": [430467901603184657, 576828535285612555, 329020569997541397],
        "players_rem": []}

maps = {"pick": ["one", "two", "three"],
        "ban": []}

bot = commands.Bot(command_prefix="=")

game_num = None
try:
    with open("data.json", "r") as file:
        info_dict = json.load(file)
        game_num = len(info_dict.keys()) + 1
except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
    game_num = 0
    

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="j", aliases=["join"])
async def join(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    
    if ctx.author.id not in queue["players"]:
        queue["players"].append(ctx.author.id)

    # prints players in queue while its not full
    if len(queue["players"]) != options["max_players"]:
        embed = discord.Embed(
            title=f"In queue [{len(queue['players'])}/{(options['max_players'])}] #{game_num}", 
            # prints out name of players joined with index
            description="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(queue["players"], start=1)), 
            color=0x00FF00)
        await ctx.send(embed=embed)

    # splist group of max_players into two, then prints out the two groups
    if len(queue["players"]) >= options["max_players"]:
        if options["random"] == True:
            
            info["team1"] = random.sample(queue["players"], int(options["max_players"]/2))
            info["team2"] = list(set(queue["players"]) - set(info["team1"]))
            
            team1 = "\n".join(f"<@{player}>" for player in info["team1"])
            team2 = "\n".join(f"<@{player}>" for player in info["team2"])
            embed = discord.Embed(
            title=f"#{game_num} Teams", 
                description="Team 1\n" + team1 + "\nTeam 2\n" + team2, 
                color=0xFF5500)
            embed.add_field(name="Map",value=random.choice(maps['pick']), inline=False)

            await ctx.send(embed=embed)
            await ctx.send("Team 1")
            await ctx.send("\n".join(f"<@{player}>" for player in info["team1"]))
            await ctx.send("Team 2")
            await ctx.send("\n".join(f"<@{player}>" for player in info['team2']))
            
        # picks random captains
        else:
            captains = random.sample(queue["players"], 2)
            info["team1"].append(captains[0])
            info["team2"].append(captains[1])
            info["captains"].clear()
            info["captains"] += captains
            queue["players_rem"] = list(set(queue["players"]) - set(captains))
            await ctx.send("Captains:")
            await ctx.send("\n".join(f"<@{captain}>" for captain in captains))
            embed = discord.Embed(title="Players to pick", description="\n".join(f"<@{player}>" for player in queue["players_rem"]),
                colour=0xFF5500)
            await ctx.send(embed=embed)
            
#   leave queue
@bot.command(name="l", aliases=["leave"])
async def leave(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if ctx.author.id in queue["players"]:
        queue["players"].remove(ctx.author.id)
        await ctx.send(f"Removed {ctx.author.name} from queue")
    else:
        await ctx.send(f"{ctx.author.name} not in queue")

#   remove player from queue
@bot.command(name="r", aliases=["remove"])
@has_permissions(administrator=True)
async def remove(ctx, player: Member=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if player == None:
        await ctx.send("```usage: =r <@player name>```")
    elif player.id in queue["players"]:
        queue["players"].remove(player.id)
        await ctx.send(f"Removed {player.name} from queue")
    else:
        await ctx.send(f"{player.name} not in queue")

#   options for max player limit and team randomisation
@bot.command(name="o", aliases=["options"])
@has_permissions(administrator=True)
async def set_options(ctx, arg1: int=None, arg2: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if arg1 == None or arg2 == None:
        await ctx.send("```usage: =o <max # of players> <t/f(true/false) for random teams(else random leaders are picked)>```")
    else:
        options["max_players"] = arg1
        arg2 = arg2.lower()
        if arg2 == "t" or arg2 == "true":
            options["random"] = True
        elif arg2 == "f"or arg2 == "false":
            options["random"] = False
        embed = discord.Embed(description=f"Max players: {options['max_players']}\nRandomise teams: {options['random']}",colour=0x00FFFF)
        await ctx.send(embed=embed)

#   pick player from list by team captain
@bot.command(name="p", aliases=["pick", "choose"])
async def pick(ctx, player: Member=None, player2: Member=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if player == None:
        await ctx.send("```usage: =p @player```")
    elif player.id not in queue["players_rem"]:
        await ctx.send("Player not in roster")
    elif ctx.author.id not in info["captains"]:
        await ctx.send("You not a captain m8 :rage:")
    elif len(info["team1"]) == len(info["team2"]) and ctx.author.id == info["captains"][0]:
        info["team1"].append(player.id)
        queue["players_rem"].remove(player.id)
        # if only 1 players remains to be picked, place him into team automatically
        if len(queue["players_rem"]) == 1:
            info["team2"].append(queue["players_rem"][0])
            queue["players_rem"].remove(queue["players_rem"][0])
            await ctx.send(embed=team_embed())
            # sends ping to players
            await ctx.send("Team 1")
            await ctx.send("\n".join(f"<@{player}>" for player in info["team1"]))
            await ctx.send("Team 2")
            await ctx.send("\n".join(f"<@{player}>" for player in info['team2']))
            # clears queue so people can start queueueueing again
            queue["players"].clear()
        else:
            await ctx.send(embed=team_embed())
    elif len(info["team1"]) != len(info["team2"]) and ctx.author.id == info["captains"][1]:
        info["team2"].append(player.id)
        queue["players_rem"].remove(player.id)
        await ctx.send(embed=team_embed())
    else:
        await ctx.send("Tis not your turn :rage:")

#   returns an embed listing teams, players left and or captains
def team_embed():
    players_remaining = "\n".join(f"<@{player}>" for player in queue["players_rem"])
    nl = '\n'  # f string {} doesnt support backslashes(\)
    if len(info["captains"]):
        team1 = "\n".join(f"<@{player}>" for player in info["team1"][1:])
        team2 = "\n".join(f"<@{player}>" for player in info["team2"][1:])
        desc = f"***Team 1***\n**Captain:** <@{info['captains'][0]}>\n{team1}\n\n\
                ***Team 2***\n**Captain:** <@{info['captains'][1]}>\n{team2}\n\n\
                {f'**Remaining:**{nl}{players_remaining}' if queue['players_rem'] else ''}"
    else:
        team1 = "\n".join(f"<@{player}>" for player in info["team1"])
        team2 = "\n".join(f"<@{player}>" for player in info["team2"])
        desc = f"***Team 1***\n{team1}\n\n\
                ***Team 2***\n{team2}\
                {f'{nl+nl}**Remaining:**{nl}{players_remaining}' if queue['players_rem'] else ''}"
    embed = discord.Embed(title=f"#{game_num} Teams",
        description=desc,
        colour=0xFF5500)
    if len(info["team1"]) + len(info["team2"]) == options["max_players"]:
        embed.add_field(name="Map", value=random.choice(maps['pick']), inline=False)
    return embed

@bot.command(name="queue", aliases=["queueueue"])
async def get_queue(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if not queue["players"]:
        desc = r"\**crickets*\*"
    else:
        desc ="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(queue["players"], start=1))
    embed = discord.Embed(title=f"In queue [{len(queue['players'])}/{(options['max_players'])}] #{game_num}", 
            description=desc,
            colour=0x00FF00)
    await ctx.send(embed=embed)

#   list all maps
@bot.command(name="maps")
async def map_list(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    embed = discord.Embed(title="Maps",
        description="\n".join(f"[{i}] {map_string}" for i, map_string in enumerate(maps['pick'], start=1)),
        colour=0x0055FF)
    await ctx.send(embed=embed)

#   select random map
@bot.command(name="m", aliases=["map"])
async def map_random(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.send(f"map: {random.choice(maps['pick'])}")

#   add map to roster
@bot.command(name="madd", aliases=["mapadd"])
@has_permissions(administrator=True)
async def map_add(ctx, map_str: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if map_str == None:
        await ctx.send("```usage: =madd <map_name>```")
    else:
        maps["pick"].append(map_str)
        await ctx.send(f"map added: {map_str}")

#   remove map from roster
@bot.command(name="mremove", aliases=["mapremove"])
@has_permissions(administrator=True)
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

@bot.command(name="members", aliases=["players"])
async def members(ctx):
    print("\n".join(f"{str(member.id)} {member.name}" for member in ctx.guild.members))

#   adds points to selected team
@bot.command(name="w", aliases=["win"])
@has_permissions(administrator=True)
async def win(ctx, team: int=None, game: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if team == None:
        await ctx.send("```=w <winning team number> (<game number>)```")
    elif game == None:
        info["winner"] = team
        if team == 1:
            team_win = "team1"
            team_loss = "team2"
        elif team == 2:
            team_loss = "team1"
            team_win = "team2"
        else:
            await ctx.send(embed=team_embed())
            return
        for player in info[team_win]:
            # checks if not owner of server
            if player != ctx.guild.owner.id:
                # assigns points by reading and changing display name
                player = ctx.message.guild.get_member(player)
                score = int(player.display_name.split("]")[0][1:])
                await player.edit(nick=f"[{score + 10}] - {player.name}"[0:32])
        for player in info[team_loss]:
            # checks if not owner of server
            if player != ctx.guild.owner.id:
                # assigns points by reading and changing display name
                player = ctx.message.guild.get_member(player)
                score = int(player.display_name.split("]")[0][1:])
                await player.edit(nick=f"[{score - 10 if score > 0 else score}] - {player.name}"[0:32])
        
        save()
        reset_dict(queue)
        reset_dict(info)
    # second argument proveded changes that games winner 
    else:
        with open("data.json", "r+") as file:
            info_dict = json.load(file)
            info_dict[str(game)]["winner"] = team
            # sets cursor to start of file, and deletes file contents
            file.seek(0)
            file.truncate()
            json.dump(info_dict, file)

def reset_dict(dict):
    for key in dict:
        if key == "winner":
            dict[key] = None
        else:
            dict[key] = []

@bot.command(name="nick", aliases=["nic", "nickname"])
@has_permissions(administrator=True)
async def nick(ctx, member: Member=None, nick: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if member == None or nick == None:
        await ctx.send("```=nick <@name> <new_nick>```")
    if member == ctx.guild.owner:
        await ctx.send("```cant change nick of server owner```")
    await member.edit(nick=nick)

@bot.command(name="clear", aliases=["c"])
@has_permissions(administrator=True)
async def clear_queue(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    queue["players"] = []
    await ctx.send("queue cleared")

#   exits bot
@bot.command(name="q", aliases=["exit", "quit", "close"])
@has_permissions(administrator=True)
async def quit(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.bot.close()

#   prints out info dict
@bot.command(name="debug")
@has_permissions(administrator=True)
async def debug(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    print(info)

def save():
    if not os.path.exists("data.json"):
        players_copy = {}
        players_copy["1"] = info
        with open("data.json", "a") as file:
            json.dump(players_copy, file)
    else:
        # get last key in dict file
        try:
            with open("data.json", "r+") as file:
                info_dict = json.load(file)
                last_key = len(info_dict.keys())
                info_dict[f"{last_key + 1}"] = info
                # sets cursor to start of file, and deletes file contents
                file.seek(0)
                file.truncate()
                json.dump(info_dict, file)
        # if file empty
        except json.decoder.JSONDecodeError:
            with open("data.json", "a") as file:
                players_copy = {}
                players_copy["1"] = info
                with open("data.json", "a") as file:
                    json.dump(players_copy, file)

#   recalculates the players scores from data file
@bot.command(name="recalc", aliases=["rec", "re"])
@has_permissions(administrator=True)
async def recalculate_score(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    with open("data.json", "r") as file:
        player_scores = {}
        info_dict = json.load(file)

        # sets scores to 0
        for teams in info_dict.values():
            for winner in (teams["team1"] if teams["winner"] == 1 else teams["team2"]):
                player_scores[winner] = get_score(ctx, winner, 0)
        for loser in info_dict.values():
            for loser in (teams["team2"] if teams["winner"] == 1 else teams["team1"]):
                player_scores[loser] = get_score(ctx, loser, 0) 
        for player in player_scores.keys():
            if int(player) != ctx.guild.owner.id:
                player_obj = ctx.message.guild.get_member(int(player))
                await player_obj.edit(nick=f"[{player_scores[player_obj.id]}] - {player_obj.name}"[0:32])

        # sets scores from file
        for teams in info_dict.values():
            for winner in (teams["team1"] if teams["winner"] == 1 else teams["team2"]):
                player_scores[winner] += get_score(ctx, winner, 10)
        for loser in info_dict.values():
            for loser in (teams["team2"] if teams["winner"] == 1 else teams["team1"]):
                player_scores[loser] +=  get_score(ctx, loser, -10)
        for player in player_scores.keys():
            if int(player) != ctx.guild.owner.id:
                player_obj = ctx.message.guild.get_member(int(player))
                await player_obj.edit(nick=f"[{player_scores[player_obj.id]}] - {player_obj.name}"[0:32])

def get_score(ctx, player, score):
    if player != ctx.guild.owner.id:
        # assigns points by reading and changing display name
        player = ctx.message.guild.get_member(player)
        # gets score brackets w/ num
        get_score = re.search(r"^(\[[0-9]+\])", player.display_name)

        # if name doesnt have score -> set score to 10 if positive else 0
        if get_score == None:
            return 10 if score > 0 else 0
        else:
            # set score to 0 if arg is 0
            if score == 0:
                return 0
            else:
                # removes brackets
                current_score = int(re.sub(r"[\[\]]", "", get_score.group(0)))
                if score < 0 and current_score <= 0:
                    return 0
                else:
                    return current_score + score
    # returns 0 if guild owner
    else:
        return 0

bot.run(TOKEN)

#TODO option to change pick order 1-2..2-1/1-1..1-1
#TODO function to recalculate everyones score from file
#TODO allow to join queue(new empty queue) when pick phase is going on
#TODO have players receives less score for win at high score counts
#       ^take in account team & enemy players scores when giving points?
#TODO have another file? to give custom scores to players
#TODO print current game number in loby & pick phase
#   ^- only allow to set winner by game number?