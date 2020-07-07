from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions
import discord
import os
import random
import json
import re


TOKEN = os.environ.get('DOOTDOOT_TOKEN')

options = {"max_players": 6,
        "random": True,
        "pick_order": 2,
        "average": True}

# info = {"players": [235088799074484224, 690386474012639323, 714940599798726676],#, 444, 555, 666, 777, 888, 999, 123123123, 178178178178],
info = {"captains": [],
        "team1": [],
        "team2": [],
        "winner": None,
        "game_num": None}

queue = {"players": [430467901603184657, 576828535285612555, 329020569997541397, 275300089910657024, 205255385966313473],
# queue = {"players": [],
        "players_rem": []}

player_scores = {}

player_scores_bonus = {}

bot = commands.Bot(command_prefix="=")

# reads file and assigns variables to maps and game_num
try:
    with open("data.json", "r") as file:
        info_dict = json.load(file)
        info["game_num"] = len(info_dict.keys())
        maps = info_dict["maps"]
except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
    info["game_num"] = 0
    maps = []
    

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="join", aliases=["j"],  brief="join queue", description="join queue")
async def join(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    
    if ctx.author.id not in queue["players"]:
        queue["players"].append(ctx.author.id)

    # prints players in queue while its not full
    if len(queue["players"]) != options["max_players"]:
        embed = discord.Embed(
            title=f"In queue [{len(queue['players'])}/{(options['max_players'])}] #{info['game_num']}", 
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
            title=f"#{info['game_num']} Teams", 
                description="Team 1\n" + team1 + "\nTeam 2\n" + team2, 
                color=0xFF5500)
            embed.add_field(name="Map",value=random.choice(maps), inline=False)

            await ctx.send(embed=embed)
            await ctx.send("Team 1")
            await ctx.send("\n".join(f"<@{player}>" for player in info["team1"]))
            await ctx.send("Team 2")
            await ctx.send("\n".join(f"<@{player}>" for player in info['team2']))
            # clear queue
            queue["players"].clear()
            
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
            embed = discord.Embed(title=f"{'Pick one' if options['pick_order'] != 2 else 'Pick two'}",
                description="\n".join(f"<@{player}>" for player in queue["players_rem"]),
                colour=0xFF5500)
            await ctx.send(embed=embed)
            # clear queue
            queue["players"].clear()
            
#   leave queue
@bot.command(name="leave", aliases=["l"], brief="leave queue", description="leave queue")
async def leave(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if ctx.author.id in queue["players"]:
        queue["players"].remove(ctx.author.id)
        await ctx.send(f"Removed {ctx.author.name} from queue")
    else:
        await ctx.send(f"{ctx.author.name} not in queue")

#   remove player from queue
@bot.command(name="remove", aliases=["r"], brief="remove player from queue", description="remove player from queue")
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
@bot.command(name="options", aliases=["o"], brief="change queue settings",
                description="max_players: set the max ammount of players that can be in a queue\ncaptains: option to auto pick the teams or teams are selected by captains")
@has_permissions(administrator=True)
async def set_options(ctx, max_players: int=None, captains: str=None, pick_order: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if max_players == None or captains == None or pick_order == None:
        await ctx.send("```usage: =o <max # of players> <randomise teams?> <pick order 1|2>```")
        embed = discord.Embed(title="Options",
                 description=f"Max players: {options['max_players']}\nRandomise teams: {options['random']}\nPick order: {options['pick_order']}",
                 colour=0x00FFFF)
        await ctx.send(embed=embed)
    else:
        options["max_players"] = max_players
        captains = captains.lower()
        if captains == "t" or captains == "true":
            options["random"] = True
        elif captains == "f"or captains == "false":
            options["random"] = False
        options["pick_order"] = pick_order
        embed = discord.Embed(description=f"Max players: {options['max_players']}\nRandomise teams: {options['random']}\nPick order: {options['pick_order']}",
                 colour=0x00FFFF)
        await ctx.send(embed=embed)

#   pick player from list by team captain
@bot.command(name="pick", aliases=["p", "choose"], brief="captain option to pick player",
                description="the captain picks player for their team")
async def pick(ctx, player: Member=None, player2: Member=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if player == None or (options["pick_order"] == 2 and player2 == None):
        await ctx.send("```usage: =p @player (@player2)```")
    elif player.id not in queue["players_rem"] or (options["pick_order"] == 2 and player2.id not in queue["players_rem"]):
        await ctx.send("player(s) not in roster")
    elif ctx.author.id not in info["captains"] and ctx.author.id != ctx.guild.owner.id:
            await ctx.send("You not a captain m8 :rage:")
    elif len(info["team1"]) == len(info["team2"]) and (ctx.author.id == info["captains"][0] or ctx.author.id == ctx.guild.owner.id):
        info["team1"].append(player.id)
        queue["players_rem"].remove(player.id)
        # if pick_order is set to 2, add 2nd player into team
        if options["pick_order"] == 2:
            info["team1"].append(player2.id)
            queue["players_rem"].remove(player2.id)
        # if only 1 players remains to be picked, place him into team automatically
        if len(queue["players_rem"]) == 1 or (len(queue["players_rem"]) == 2 and options["pick_order"] == 2):
            info["team2"].append(queue["players_rem"][0])
            queue["players_rem"].remove(queue["players_rem"][0])
            # if pick_order is set to 2, add 2nd player into team
            if options["pick_order"] == 2:
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
    elif len(info["team1"]) != len(info["team2"]) and (ctx.author.id == info["captains"][1] or ctx.author.id == ctx.guild.owner.id):
        info["team2"].append(player.id)
        queue["players_rem"].remove(player.id)
        # if pick_order is set to 2, add 2nd player into team
        if options["pick_order"] == 2:
            info["team2"].append(player2.id)
            queue["players_rem"].remove(player2.id)
        await ctx.send(embed=team_embed())
    else:
        await ctx.send("Tis not your turn :rage:")

@bot.command(name="queue", aliases=["queueueue"], brief="displays the players in queue",
                description="display the palyers in queue")
async def get_queue(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if not queue["players"]:
        desc = r"\**crickets*\*"
    else:
        desc ="\n".join(f"[{i}] <@{player}>" for i, player in enumerate(queue["players"], start=1))
    embed = discord.Embed(title=f"In queue [{len(queue['players'])}/{(options['max_players'])}] #{info['game_num']}", 
            description=desc,
            colour=0x00FF00)
    await ctx.send(embed=embed)

#   list all maps
@bot.command(name="maps", brief="displays selectable maps", description="displays selectable maps")
async def map_list(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    embed = discord.Embed(title="Maps",
        description="\n".join(f"[{i}] {map_string}" for i, map_string in enumerate(maps, start=1)),
        colour=0x0055FF)
    await ctx.send(embed=embed)

#   select random map
@bot.command(name="map", aliases=["m"], brief="randomly selects map", description="randomly selects map")
async def map_random(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.send(f"map: {random.choice(maps)}")

#   add map to roster
@bot.command(name="mapadd", aliases=["madd", "ma"], brief="adds map to selection", description="adds map to selection")
@has_permissions(administrator=True)
async def map_add(ctx, map_str: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if map_str == None:
        await ctx.send("```usage: =madd <map_name>```")
    else:
        maps.append(map_str)
        with open("data.json", "r+") as file:
            info_dict = json.load(file)
            info_dict["maps"] = maps
            # sets cursor to start of file, and deletes file contents
            file.seek(0)
            file.truncate()
            json.dump(info_dict, file)
        await ctx.send(f"map added: {map_str}")

#   remove map from roster
@bot.command(name="mapremove", aliases=["mremove", "mrem", "mr"], brief="removes map from selection", description="removes map from selection")
@has_permissions(administrator=True)
async def map_remove(ctx, map_int: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if map_int == None:
        print(len(maps))
        await ctx.send("```usage: =mapremove <map_number>```")
    elif len(maps) < map_int:
        await ctx.send("""```diff\n- map number out of range```""")
    else:
        await ctx.send(f"map removed: {maps[map_int - 1]}")
        del maps[map_int - 1]
        with open("data.json", "r+") as file:
            info_dict = json.load(file)
            info_dict["maps"] = maps
            # sets cursor to start of file, and deletes file contents
            file.seek(0)
            file.truncate()
            json.dump(info_dict, file)

@bot.command(name="whoami", brief="displays your name and id", description="displays your name and id")
async def whoami(ctx):
    await ctx.send(f"<@{ctx.author.name}\n{ctx.author.id}\n{ctx.author}>")

@bot.command(name="members", aliases=["players"], brief="displays all members in guild",
                description="displays all members in guild")
async def members(ctx):
    print("\n".join(f"{str(member.id)} {member.name}" for member in ctx.guild.members))

#   adds points to selected team
@bot.command(name="win", aliases=["w"], brief="selects which team won the game", description="selects which team won the game if game number provided")
@has_permissions(administrator=True)
async def win(ctx, team: int=None, game_number: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if team == None:
        await ctx.send("```=w <winning team number> (<game number>)```")
    elif game_number == None:
        info["winner"] = team
        sum_win = 0
        sum_loss = 0
        if team == 1:
            team_win = "team1"
            team_loss = "team2"
        elif team == 2:
            team_loss = "team1"
            team_win = "team2"
        else:
            await ctx.send(embed=team_embed())
            return

        # get sums
        if options["average"] != False:
            for player in info[team_win]:
                sum_win += get_score_from_id(ctx, player)

            for player in info[team_loss]:
                sum_loss += get_score_from_id(ctx, player)

        # calcualtes the average
        if sum_win != 0 and sum_loss != 0 and options["average"] != False:
            average = round(sum_loss/sum_win * 10)
        else:
            average = 10

        for player in info[team_win]:
            # checks if not owner of server
            score = get_score_from_id(ctx, player)
            player = get_player_obj(ctx, player)
            if player != ctx.guild.owner:
                if score != 0:
                    await player.edit(nick=f"[{score + average}] - {player.name}"[0:32])
                else:
                    await player.edit(nick=f"[10] - {player.name}"[0:32])

        for player in info[team_loss]:
            # checks if not owner of server
            score = get_score_from_id(ctx, player)
            player = get_player_obj(ctx, player)
            if player != ctx.guild.owner:
                if score != 0:
                    await player.edit(nick=f"[{score - average if (score - average) > 0 else score}] - {player.name}"[0:32])
                else:
                    await player.edit(nick=f"[0] - {player.name}"[0:32])

        save()
        reset_dict(queue)
        reset_dict(info)
    # second argument proveded changes that games winner 
    else:
        with open("data.json", "r+") as file:
            info_dict = json.load(file)
            info_dict[str(info["game_num"])]["winner"] = team
            # sets cursor to start of file, and deletes file contents
            file.seek(0)
            file.truncate()
            json.dump(info_dict, file)

@bot.command(name="nickname", aliases=["nic", "nick"], brief="change your nickname", description="change your nickname")
@has_permissions(administrator=True)
async def nick(ctx, member: Member=None, nick: str=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if member == None or nick == None:
        await ctx.send("```=nick <@name> <new_nick>```")
    if member == ctx.guild.owner:
        await ctx.send("```cant change nick of server owner```")
    await member.edit(nick=nick)

@bot.command(name="clear", aliases=["c"], brief="clears queue", description="clears queue")
@has_permissions(administrator=True)
async def clear_queue(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    queue["players"].clear()
    await ctx.send("queue cleared")

#   exits bot
@bot.command(name="quit", aliases=["q", "exit", "close"], brief="stops the bot script", description="stops the bot script")
@has_permissions(administrator=True)
async def quit(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    await ctx.bot.close()

#   recalculates the players scores from data file
@bot.command(name="recalc", aliases=["rec", "re"], brief="re-calculates everyones score", 
                description="re-calculates everyones score from file")
@has_permissions(administrator=True)
async def recalculate_score(ctx):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    with open("data.json", "r") as file:
        player_scores.clear()
        info_dict = json.load(file)
        # ignores the "points" key as that contains the extra points dict
        values = list(info_dict.values())[2:]

        # sets scores to 0
        for teams in values:
            for player in teams["team1"]:
                player_scores[player] = 0
            for player in teams["team2"]:
                player_scores[player] = 0
        
        # sets nicknames to 0
        for player in player_scores.keys():
            if player != ctx.guild.owner.id:
                player_obj = get_player_obj(ctx, player)
                await player_obj.edit(nick=f"[0] - {player_obj.name}"[0:32])

        # sets scores from file
        for teams in values:
            # sets sums to 0 on every new game
            sum_win = 0
            sum_loss = 0

            if options["average"] != False:
                for winner in (teams["team1"] if teams["winner"] == 1 else teams["team2"]):
                    # make another dict to hold scores for teams of only 1 game -> then average those scores
                    sum_win += player_scores[winner]

                for loser in (teams["team2"] if teams["winner"] == 1 else teams["team1"]):
                    sum_loss += player_scores[loser]

            # calcualtes the average
            if sum_win != 0 and sum_loss != 0 and options["average"] != False:
                average = round(sum_loss/sum_win * 10)
            else:
                average = 10

            for winner in (teams["team1"] if teams["winner"] == 1 else teams["team2"]):
                player_scores[winner] +=  average

            for loser in (teams["team2"] if teams["winner"] == 1 else teams["team1"]):
                if player_scores[loser] - average > 0:
                    player_scores[loser] -=  average

        # adds the extra scores
        for player in info_dict["points"].keys():
            player_scores[int(player)] += info_dict["points"][player]
        # changes the nicknames in discord
        for player in player_scores.keys():
            if int(player) != ctx.guild.owner.id:
                player_obj = ctx.message.guild.get_member(int(player))
                await player_obj.edit(nick=f"[{player_scores[player_obj.id]}] - {player_obj.name}"[0:32])

#   gives player points
@bot.command(name="give", aliases=["g", "points"], brief="gives player points", 
                description="gives player points")
@has_permissions(administrator=True)
async def give_points(ctx, player: Member=None, points: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if player == None or points == None:
        await ctx.send("```=give <@name> <points to give>```")
        return
    info_dict = {}
    try:
        with open("data.json", "r") as file:
            info_dict = json.load(file)
            extra_scores = info_dict["points"]
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        extra_scores = {}
    if player.id not in player_scores_bonus:
        extra_scores[str(player.id)] = points
    else:
        extra_scores[str(player.id)] += points
    print(extra_scores)
    for player in extra_scores.keys():
        if extra_scores[player] == None:
            extra_scores[player] = 0
        if int(player) != ctx.guild.owner.id:            
            player_obj = ctx.message.guild.get_member(int(player))
            score_from_name = re.search(r"^(\[[0-9]+\])", player_obj.display_name)
            if score_from_name != None:
                # removes brackets
                score_from_name = int(re.sub(r"[\[\]]", "", score_from_name.group(0)))
                if score_from_name + extra_scores[player] > 0:
                    new_score = score_from_name + extra_scores[player]
                else:
                    new_score = 0
                await player_obj.edit(nick=f"[{new_score}] - {player_obj.name}"[0:32])
    with open("data.json", "w") as file:
        info_dict["points"] = extra_scores
        json.dump(info_dict, file)

#   rolls x sided dice
@bot.command(name="roll", brief="rolls an x sided dice",
             description="rolls a dice of argument <sides> sided dice. If no argument - rolls 2 sided dice")
async def roll(ctx, sides: int=None):
    if ctx.author == bot.user or ctx.channel.name != "bot":
        return
    if sides == None:
        await ctx.send(random.randrange(1,3))
        return
    await ctx.send(random.randrange(1,sides))

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
    embed = discord.Embed(title=f"#{info['game_num']} Teams",
        description=desc,
        colour=0xFF5500)
    if len(info["team1"]) + len(info["team2"]) == options["max_players"]:
        embed.add_field(name="Map", value=random.choice(maps), inline=False)
    return embed

def get_score_from_id(ctx, player_id):
    if player_id != ctx.guild.owner.id:
        # gets player object 
        player = ctx.message.guild.get_member(player_id)
        score = re.search(r"^(\[[0-9]+\])", player.display_name)
        if score != None:
            # removes brackets
            score = int(re.sub(r"[\[\]]", "", score.group(0)))
            return score
        else:
            return 0
    else:
        return 0

def reset_dict(dict):
    for key in dict:
        if key == "winner":
            dict[key] = None
        elif key == "game_num":
            dict[key] += 1
        else:
            dict[key].clear()

def get_score(ctx, player, score, average):
    if player != ctx.guild.owner.id:
        player = get_player_obj(ctx, player)
        # gets score brackets w/ num
        get_score = re.search(r"^(\[[0-9]+\])", player.display_name)

        # if name doesnt have score -> set score to 10 if positive else 0
        if get_score == None:
            return 10 if score > 0 else 0
        else:
            # set score to 0 if score arg is 0
            if score == 0:
                return 0
            else:
                if player_scores[player.id] + score >= 0:
                    return score
                else:
                    return 0
    # returns 0 if guild owner
    else:
        return 0

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
                num_of_keys = len(info_dict.keys())
                info_dict[f"{num_of_keys}"] = info
                # before writing, sets cursor to start of file, and deletes file contents
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

def get_player_obj(ctx, player_id):
    return ctx.message.guild.get_member(player_id)


if __name__ == "__main__":
    bot.run(TOKEN)
