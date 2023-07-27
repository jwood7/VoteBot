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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$last_maps'):
        # url = "http://192.168.0.209:8000/api/stats/botrating/"
        url = "http://stats.geekfestclan.com/api/stats/botrating/"
        # send vote of -1 to api to check if map is valid (200 response or content of map is valid)
        response = requests.post(url, json = {"map": "last_maps", "user": message.author.name, "rating": -2, "key": os.getenv('KEY')})
        maps = json.loads(response.text)
        await message.channel.send('The last 3 maps are: '+ maps[0]["map"] + ', '+ maps[1]["map"] + ', and ' + maps[2]["map"] +'\n$vote [map_name], then vote for the map on a scale of 1️⃣ - 5️⃣!')
    elif message.content.startswith('$lookup'):
        if (len(message.content.split(' ')) < 2):
            await message.channel.send('$lookup [map_name] to search for a map name')
        else:
            map_name = message.content.split(' ')[1]
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
    elif message.content.startswith('$vote'):
        if (len(message.content.split(' ')) < 2):
            await message.channel.send('$vote [map_name], then vote for the map on a scale of 1️⃣ - 5️⃣!\n$last_maps to see the last 3 maps.\n$lookup [map_name] to search for a map name')
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
                    # vote_msg = await message.channel.send('Vote on ' + maps[0]["map"])
                    embed = discord.Embed(title = 'Vote on ' + maps[0]["map"], 
                                          description = 'Vote for the map on a scale of 1️⃣ - 5️⃣!', 
                                          color = 0x00ff00,
                                          url = 'http://stats.geekfestclan.com/stats/Map2?mid=' + str(maps[0]["idmap"]))
                                        #   url = 'http://192.168.0.209:8000/api/stats/Map2?mid=' + str(maps[0]["idmap"]))
                    if (maps[0]["description"]):
                        embed.add_field(name = 'Map description', value = maps[0]["description"], inline = False)
                    if (maps[0]["thumbnail"]):
                        embed.set_image(url = "http://stats.geekfestclan.com/media/" + maps[0]["thumbnail"])
                    else:
                        embed.set_image(url = "http://stats.geekfestclan.com/static/images/map_not_found.jpg")
                    vote_msg = await message.channel.send(embed = embed)
                    try:
                        await vote_msg.add_reaction("1️⃣")
                        await vote_msg.add_reaction("2️⃣")
                        await vote_msg.add_reaction("3️⃣")
                        await vote_msg.add_reaction("4️⃣")
                        await vote_msg.add_reaction("5️⃣")
                    except:
                        print("error adding reactions")
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
            # If response invalid, send error message
            if response.content and response.status_code != 201: 
                await reaction.message.channel.send('Map "' + map_name + ' or Geek "' + user.name + '" not found.')

client.run(os.getenv('TOKEN'))