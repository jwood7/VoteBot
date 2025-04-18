import discord
from discord import app_commands
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
tree = app_commands.CommandTree(client)

async def embed_map(map_dict, channel): #used to embed and send map info
    # Since the new API returns data in maps[0], ensure we're using the correct object
    map_data = map_dict["maps"][0] if "maps" in map_dict else map_dict
    
    embed = discord.Embed(title = 'Vote on ' + map_data["map"], 
                         description = 'Vote for the map on a scale of 1️⃣ - 5️⃣!', 
                         color = 0x00ff00,
                         url = 'https://newgeekfeststats.duckdns.org/stats/maps/' + str(map_data["idmap"]) + '/')
    
    if (map_data["description"]):
        embed.add_field(name = 'Map description', value = map_data["description"], inline = False)
    
    if (map_data["thumbnail"]):
        embed.set_image(url = "https://newgeekfeststats.duckdns.org/media/" + map_data["thumbnail"])
        print("thumbnail: " + map_data["thumbnail"])
    else:
        embed.set_image(url = "https://newgeekfeststats.duckdns.org/static/images/map_not_found.jpg")
    
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
@tree.command(
    name="check",
    description="Check the rating of a map",
    guild=discord.Object(id=533307442189172737)
)
@app_commands.describe(map_name="Name of the map being checked")
async def check(interaction, map_name: str):
    url = "http://stats.geekfestclan.com/api/stats/botrating/"
    response = requests.post(url, json = {"map": map_name, "user": interaction.user.name, "rating": -3, "key": os.getenv('KEY')})
    maps = json.loads(response.text)
    if response.content and response.status_code == 200:
        if len(maps) > 0:
            try:
                await interaction.response.send_message(str(maps[0]["map_name"]) + ' has a rating of ' + str(maps[0]["vote_sum"]/(maps[0]["vote_count"]* 5 )* 100)[:6] + ' from ' + str(maps[0]["vote_count"]) + ' votes. OLD STATS')
            except:
                print("error sending message")
        else:
            await interaction.response.send_message('Map "' + map_name + '" not found.')
    else:
        await interaction.response.send_message('Map "' + map_name + '" not found.')
@tree.command(
    name="last_maps",
    description="Check the last three maps played - OLD STATS",
    guild=discord.Object(id=533307442189172737)
)
async def last_maps(interaction):
    url = "http://stats.geekfestclan.com/api/stats/botrating/"
    response = requests.post(url, json = {"map": "last_maps", "user": interaction.user.name, "rating": -2, "key": os.getenv('KEY')})
    maps = json.loads(response.text)
    await interaction.response.send_message("Sending last three maps", ephemeral=True)
    for i in range(len(maps)-1,-1,-1):
        try:
            await embed_map(maps[i], interaction.channel)
        except:
            print("error embedding map" + " " + str(i) + " " + maps[i]["map"])
    # await interaction.response.send_message("Last three maps sent", ephemeral=True)
@tree.command(
    name="lookup",
    description="Search for a map",
    guild=discord.Object(id=533307442189172737)
)
@app_commands.describe(map_name="Name of the map being searched")
async def lookup(interaction, map_name: str):
    url = f"https://newgeekfeststats.duckdns.org/api/maps/maps/?map={map_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        map_data = response.json()
        if map_data["maps"] and len(map_data["maps"]) > 0:
            map_list = ''
            for map in map_data["maps"]:
                # Add CS2 indicator if the map is CS2
                cs2_indicator = " (CS2)" if map["cs2"] else ""
                # Add workshop indicator if it has a workshop number
                workshop_indicator = " [Workshop]" if map["workshop_map_nbr"] else ""
                map_list = map_list + map["map"] + cs2_indicator + workshop_indicator + ', '
            await interaction.response.send_message('Found the following cs2 maps: ' + map_list[:-2] + '\n')
        else:
            await interaction.response.send_message(f'Map "{map_name}" not found.')
    else:
        await interaction.response.send_message(f'Error looking up map "{map_name}"')

@tree.command(
    name="vote",
    description="Vote for a map",
    guild=discord.Object(id=533307442189172737)
)
@app_commands.describe(map_name="Name of the map being voted on")
async def vote(interaction, map_name:str='' ):
    if map_name == '':
        await interaction.response.send_message("/vote [map_name], then vote for the map on a scale of 1️⃣ - 5️⃣!\n/last_maps to see the last 3 maps.\n/lookup [map_name] to search for a map name\n/check [map_name] to check a map's rating")
    else:
        url = f"https://newgeekfeststats.duckdns.org/api/maps/maps/?map={map_name}&name_exact_match=true"
        # url = f"https://newgeekfeststats.duckdns.org/api/maps/maps/?map={map_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            map_data = response.json()
            if map_data["maps"] and len(map_data["maps"]) > 0:
                try:
                    await embed_map(map_data, interaction.channel)
                    await interaction.response.send_message("Vote in the below embed:", ephemeral=True)
                except Exception as e:
                    print(f"error embedding map: {e}")
            else:
                await interaction.response.send_message(f'Map "{map_name}" not found.')
        else:
            await interaction.response.send_message(f'Map "{map_name}" not found.')

@tree.command(
    name="workshopid",
    description="Get the workshop id for a map",
    guild=discord.Object(id=533307442189172737)
)
@app_commands.describe(map_name="Name of the map being searched")
async def workshopid(interaction, map_name: str=''):
    if (len(map_name) < 1):
        await interaction.response.send_message('/workshopid [map_name] to search the command to switch to a workshop map')
    else:
        url = f"https://newgeekfeststats.duckdns.org/api/maps/maps/?map={map_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            map_data = response.json()
            if map_data["maps"] and len(map_data["maps"]) > 0:
                # Find the first map with a workshop number that best matches the search
                workshop_map = None
                for map in map_data["maps"]:
                    if map["workshop_map_nbr"]:
                        if not workshop_map or len(map["map"]) < len(workshop_map["map"]):
                            workshop_map = map
                
                if workshop_map and workshop_map["workshop_map_nbr"]:
                    await interaction.response.send_message(
                        f'**Map:** {workshop_map["map"]}'
                        f'{" (CS2)" if workshop_map["cs2"] else ""} '
                        f'**RCON:** host_workshop_map {workshop_map["workshop_map_nbr"]}\n'
                    )
                else:
                    await interaction.response.send_message(f'Map "{map_name}" does not have a workshop id.')
            else:
                await interaction.response.send_message(f'Map "{map_name}" not found.')
        else:
            await interaction.response.send_message(f'Error looking up map "{map_name}"')

@tree.command(
    name="gf_sync",
    description="Syncs geekfest commands with discord autocomplete",
    guild=discord.Object(id=533307442189172737)
)
async def gf_sync(interaction):
    await tree.sync(guild=discord.Object(id=533307442189172737))
    await interaction.response.send_message("Commands synced", ephemeral=True)



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# for supporting $ commands 
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$check'): #check score of map 
        if (len(message.content.split(' ')) < 2):
            await message.channel.send("$check [map_name] to check a map's rating")
        else:
            map_name = message.content.split(' ')[1]
            # url = os.getenv('IP') + "/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -3, "key": os.getenv('KEY')})
            maps = json.loads(response.text)
            if response.content and response.status_code == 200:
                if len(maps) > 0:
                    try:
                        await message.channel.send(str(maps[0]["map_name"]) + ' has a rating of ' + str(maps[0]["vote_sum"]/(maps[0]["vote_count"]* 5 )* 100)[:6] + ' from ' + str(maps[0]["vote_count"]) + ' votes. OLD STATS')
                    except:
                        print("error sending message")
                else:
                    await message.channel.send('Map "' + map_name + '" not found.')
            else:
                await message.channel.send('Map "' + map_name + '" not found.')
    if message.content.startswith('$last_maps'): #send back last three maps played
        # url = os.getenv('IP') + "/api/stats/botrating/"
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

    elif message.content.startswith('$lookup') or message.content.startswith('/lookup'): #search for map name
        if (len(message.content.split(' ')) < 2):
            await message.channel.send('$lookup [map_name] to search for a map name')
        else:
            map_name = message.content.split(' ')[1]
            # url = os.getenv('IP') + "/api/stats/botrating/"
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
            # url = os.getenv('IP') + "/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            # send vote of -1 to api to check if map is valid (200 response or content of map is valid)
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -1, "key": os.getenv('KEY'), "name_exact_match": True})
            # response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -1, "key": os.getenv('KEY')})
            maps = json.loads(response.text)
            if response.content and response.status_code == 200:
                if len(maps) > 0:
                    try:
                        await message.delete()
                    except:
                        print("error deleting message")
                    try:
                        shortest_map = maps[0]
                        for map in maps:
                            if len(map["map"]) < len(shortest_map["map"]):
                                shortest_map = map
                        await embed_map(shortest_map, message.channel)
                    except:
                        print("error embedding map" + maps[0]["map"])
                else:
                    await message.channel.send('Map "' + map_name + '" not found.')
            else:
                await message.channel.send('Map "' + map_name + '" not found.')

    elif message.content.startswith('$workshopid') or message.content.startswith('/workshopid'): #search for map name
        if (len(message.content.split(' ')) < 2):
            await message.channel.send('$workshopid [map_name] to search the command to switch to a workshop map')
        else:
            map_name = message.content.split(' ')[1]
            # url = os.getenv('IP') + "/api/stats/botrating/"
            url = "http://stats.geekfestclan.com/api/stats/botrating/"
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -4, "key": os.getenv('KEY')})
            maps = json.loads(response.text)
            if response.content and response.status_code == 200:
                if len(maps) > 0:
                    shortest_map = maps[0]
                    for map in maps:
                        if (shortest_map["workshop_map_nbr"] == None or len(map["map"]) < len(shortest_map["map"])) and map["workshop_map_nbr"] != None:
                            shortest_map = map
                    if shortest_map["workshop_map_nbr"] != None:
                        await message.channel.send('**Map:** ' +  shortest_map["map"] + ' **RCON:** host_workshop_map ' + shortest_map["workshop_map_nbr"] + '\n')
                    else:
                        await message.channel.send('Map "' + map_name + '" does not have a map id.')
                else:
                    await message.channel.send('Map "' + map_name + '" not found.')
            else:
                await message.channel.send('Map "' + map_name + '" not found.')

    elif message.content.startswith('$gf_sync'):
        await tree.sync(guild=discord.Object(id=533307442189172737))

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
            # First, get the map_id using the maps API
            maps_url = f"https://newgeekfeststats.duckdns.org/api/maps/maps/?map={map_name}"
            maps_response = requests.get(maps_url)
            
            if maps_response.status_code == 200:
                maps_data = maps_response.json()
                if maps_data["maps"] and len(maps_data["maps"]) > 0:
                    map_id = maps_data["maps"][0]["idmap"]
                    
                    # Now submit the rating using the map-rating POST API with query parameters
                    rating_url = f"https://newgeekfeststats.duckdns.org/api/maps/map-rating/?map_id={map_id}&rating={rating}&discord_name={user.name}&discord_key={os.getenv('DISCORD_BOT_KEY')}"
                    rating_response = requests.post(rating_url)
                    
                    print(f"{user.name} added {rating} to map {map_name} (ID: {map_id})")
                    
                    if rating_response.status_code >= 400:  # Check for error status codes
                        print(f"Rating error: {rating_response.text}")
                        await reaction.message.channel.send(f'Error submitting rating for map "{map_name}"')
                else:
                    await reaction.message.channel.send(f'Map "{map_name}" not found.')
            else:
                await reaction.message.channel.send(f'Error looking up map "{map_name}"')

client.run(os.getenv('TOKEN'))