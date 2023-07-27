import discord
import os
from dotenv import load_dotenv
import requests

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

    if message.content.startswith('$vote'):
        if (len(message.content.split(' ')) < 2):
            await message.channel.send('$vote [map_name], then Vote for the map on a scale of 1️⃣ - 5️⃣!')
        else:
            map_name = message.content.split(' ')[1]
            url = "http://192.168.0.209:8000/api/stats/botrating/"
            # url = "http://stats.geekfestclan.com/api/stats/botrating/"
            # send vote of -1 to api to check if map is valid (200 response or content of map is valid)
            response = requests.post(url, json = {"map": map_name, "user": message.author.name, "rating": -1})
            if response.content and response.status_code == 200:
                try:
                    await message.add_reaction("1️⃣")
                    await message.add_reaction("2️⃣")
                    await message.add_reaction("3️⃣")
                    await message.add_reaction("4️⃣")
                    await message.add_reaction("5️⃣")
                except:
                    print("error adding reactions")
            else:
                await message.channel.send('Map "' + map_name + '" not found.')
@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author != client.user and user != client.user and reaction.message.content.startswith('$vote'):
        map_name = reaction.message.content.split(' ')[1]
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
            print(user.name + " added " + str(rating) + " to map " + map_name)
            
            # url = "http://stats.geekfestclan.com/api/stats/rating/"
            url = "http://192.168.0.209:8000/api/stats/botrating/"
            # url = "http://stats.geekfestclan.com/api/stats/botrating/"
            response = requests.post(url, json = {"map": map_name, "user": user.name, "rating": rating})
            print('api response text:  ',response.text)
            # If response invalid, send error message
            if response.content and response.status_code != 201: 
                await reaction.message.channel.send('Map "' + map_name + ' or Geek "' + user.name + '" not found.')

client.run(os.getenv('TOKEN'))