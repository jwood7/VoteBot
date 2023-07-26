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
            await message.channel.send('$vote [map_id], then Vote for the map on a scale of 1️⃣ - 5️⃣!')
        else:
            await message.add_reaction("1️⃣")
            await message.add_reaction("2️⃣")
            await message.add_reaction("3️⃣")
            await message.add_reaction("4️⃣")
            await message.add_reaction("5️⃣")

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author != client.user and user != client.user and reaction.message.content.startswith('$vote'):
        map_name = reaction.message.content.split(' ')[1]
        rating = 0
        if (reaction.emoji == "1️⃣"): rating = 1
        elif (reaction.emoji == "2️⃣"): rating = 2
        elif (reaction.emoji == "3️⃣"): rating = 3
        elif (reaction.emoji == "4️⃣"): rating = 4
        elif (reaction.emoji == "5️⃣"): rating = 5
        if rating > 0:
            print(user.name + " added " + str(rating) + " to map " + map_name)
            
            url = "http://stats.geekfestclan.com/api/stats/rating/"
            response = requests.post(url, json = {"map_id": map_name, "user_id": 18, "rating": rating})
            print('api response:  ',response)
            print('api response text:  ',response.text)
# @client.event
# async def on_reaction_remove(reaction, user):
#     if reaction.message.author == client.user:
#         map_name = reaction.message.content.split(':')[0]
#         if (reaction.emoji == "1️⃣"):
#             print(user.name + " removed 1 from " + map_name)
#         elif (reaction.emoji == "2️⃣"):
#             print(user.name + " removed 2 from " + map_name)
#         elif (reaction.emoji == "3️⃣"):
#             print(user.name + " removed 3 from " + map_name)
#         elif (reaction.emoji == "4️⃣"):
#             print(user.name + " removed 4 from " + map_name)
#         elif (reaction.emoji == "5️⃣"):
#             print(user.name + " removed 5 from " + map_name)
#         else:
#             print("invalid reaction")

client.run(os.getenv('TOKEN'))