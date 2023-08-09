import discord
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

intents=discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
client = discord.Client(intents=intents)

async def embed_map(map_dict, channel): #used to embed and send map info
    embed = discord.Embed(title = 'Vote on ' + map_dict["map"], 
                            description = 'Vote for the map on a scale of 1️⃣ - 5️⃣!', 
                            color = 0x00ff00,
                            url = 'http://stats.geekfestclan.com/stats/Map2?mid=' + str(map_dict["idmap"]))
    if (map_dict["description"]):
        embed.add_field(name = 'Map description', value = map_dict["description"], inline = False)
    if (map_dict["thumbnail"]):
        embed.set_image(url = "http://stats.geekfestclan.com/media/" + map_dict["thumbnail"])
    else:
        embed.set_image(url = "http://stats.geekfestclan.com/static/images/map_not_found.jpg")
    try:
        vote_msg = await channel.send(embed = embed)
        try:
            await vote_msg.add_reaction("1️⃣")
            await vote_msg.add_reaction("2️⃣")
            await vote_msg.add_reaction("3️⃣")
            await vote_msg.add_reaction("4️⃣")
            await vote_msg.add_reaction("5️⃣")
        except:
            print("error adding reactions")
    except:
        print("error sending embed")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$check'): #check score of map 
        if (len(message.content.split(' ')) < 2):
            await message.channel.send("$check [map_name] to check a map's rating")
        else:
            map_name = message.content.split(' ')[1]
            # url = "http://192.168.0.209:8000/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -3, "key": os.getenv('KEY')})
            maps = json.loads(response.text)
            if response.content and response.status_code == 200:
                if len(maps) > 0:
                    try:
                        await message.channel.send(str(maps[0]["map_name"]) + ' has a rating of ' + str(maps[0]["vote_sum"]/(maps[0]["vote_count"]* 5 )* 100) + ' from ' + str(maps[0]["vote_count"]) + ' votes.')
                    except:
                        print("error sending message")
                else:
                    await message.channel.send('Map "' + map_name + '" not found.')
            else:
                await message.channel.send('Map "' + map_name + '" not found.')
    if message.content.startswith('$last_maps'): #send back last three maps played
        # url = "http://192.168.0.209:8000/api/stats/botrating/"
        url = "http://stats.geekfestclan.com/api/stats/botrating/"
        response = requests.post(url, json = {"map": "last_maps", "user": message.author.name, "rating": -2, "key": os.getenv('KEY')})
        maps = json.loads(response.text)
        for i in range(len(maps)-1,-1,-1):
            try:
                await embed_map(maps[i], message.channel)
            except:
                print("error embedding map" + " " + str(i) + " " + maps[i]["map"])
        try:
            await message.delete()
        except:
            print("error deleting message")

    elif message.content.startswith('$lookup'): #search for map name
        if (len(message.content.split(' ')) < 2):
            await message.channel.send('$lookup [map_name] to search for a map name')
        else:
            map_name = message.content.split(' ')[1]
            # url = "http://192.168.0.209:8000/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -1, "key": os.getenv('KEY')})
            maps = json.loads(response.text)
            if response.content and response.status_code == 200:
                if len(maps) > 0:
                    map_list = ''
                    for map in maps:
                        map_list = map_list + map["map"] + ', '
                    await message.channel.send('Found the following maps: ' + map_list[:-2] + '\n')
                else:
                    await message.channel.send('Map "' + map_name + '" not found.')
            else:
                await message.channel.send('Map "' + map_name + '" not found.')

    elif message.content.startswith('$vote'): #vote for map
        if (len(message.content.split(' ')) < 2):
            await message.channel.send("$vote [map_name], then vote for the map on a scale of 1️⃣ - 5️⃣!\n$last_maps to see the last 3 maps.\n$lookup [map_name] to search for a map name\n$check [map_name] to check a map's rating")
        else:
            map_name = message.content.split(' ')[1]
            # url = "http://192.168.0.209:8000/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            # send vote of -1 to api to check if map is valid (200 response or content of map is valid)
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -1, "key": os.getenv('KEY')})
            maps = json.loads(response.text)
            if response.content and response.status_code == 200:
                if len(maps) > 0:
                    try:
                        await message.delete()
                    except:
                        print("error deleting message")
                    try:
                        await embed_map(maps[0], message.channel)
                    except:
                        print("error embedding map" + maps[0]["map"])
                else:
                    await message.channel.send('Map "' + map_name + '" not found.')
            else:
                await message.channel.send('Map "' + map_name + '" not found.')

@client.event
async def on_reaction_add(reaction, user):
    # this will need to change to only check reactions to the bot's messages
    if reaction.message.author == client.user and user != client.user and reaction.message.embeds:
        map_name = reaction.message.embeds[0].title.split(' ')[2]
        rating = 0
        if (reaction.emoji == "1️⃣"): 
            rating = 1
            try:
                await reaction.message.remove_reaction("2️⃣", user)
                await reaction.message.remove_reaction("3️⃣", user)
                await reaction.message.remove_reaction("4️⃣", user)
                await reaction.message.remove_reaction("5️⃣", user)
            except:
                print("error removing reactions")
        elif (reaction.emoji == "2️⃣"): 
            rating = 2
            try:
                await reaction.message.remove_reaction("1️⃣", user)
                await reaction.message.remove_reaction("3️⃣", user)
                await reaction.message.remove_reaction("4️⃣", user)
                await reaction.message.remove_reaction("5️⃣", user)
            except:
                print("error removing reactions")
        elif (reaction.emoji == "3️⃣"): 
            rating = 3
            try:
                await reaction.message.remove_reaction("1️⃣", user)
                await reaction.message.remove_reaction("2️⃣", user)
                await reaction.message.remove_reaction("4️⃣", user)
                await reaction.message.remove_reaction("5️⃣", user)
            except:
                print("error removing reactions")
        elif (reaction.emoji == "4️⃣"): 
            rating = 4
            try:
                await reaction.message.remove_reaction("1️⃣", user)
                await reaction.message.remove_reaction("2️⃣", user)
                await reaction.message.remove_reaction("3️⃣", user)
                await reaction.message.remove_reaction("5️⃣", user)
            except:
                print("error removing reactions")
        elif (reaction.emoji == "5️⃣"): 
            rating = 5
            try:
                await reaction.message.remove_reaction("1️⃣", user)
                await reaction.message.remove_reaction("2️⃣", user)
                await reaction.message.remove_reaction("3️⃣", user)
                await reaction.message.remove_reaction("4️⃣", user)
            except:
                print("error removing reactions")
        if rating > 0:
            # url = "http://stats.geekfestclan.com/api/stats/rating/"
            # url = "http://192.168.0.209:8000/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            response = requests.post(url, json = {"map": map_name, "user": user.name, "rating": rating, "key": os.getenv('KEY')})
            print(user.name + " added " + str(rating) + " to map " + map_name)
            if response.content and response.status_code != 201: 
                print (response.text)
                await reaction.message.channel.send('Map "' + map_name + '" or Geek "' + user.name + '" not found.')

client.run(os.getenv('TOKEN'))