import discord
import logging
import youtube_dl
from discord.ext import commands
from docs.config import token

client = commands.Bot(command_prefix = "!")

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

players = {}
queues = {}

def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()

@client.event
async def on_ready():
    print("svenBot is now online.")

@client.command(pass_context=True)
async def vol(ctx, value: int):
    server_id = ctx.message.server.id
    players[server_id].volume = value / 100
    await client.say("**Volume set to:** " + str(value) + "%")

@client.command(pass_context=True)
async def play(ctx, url):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    players[server.id] = player
    player.volume = 0.15
    player.start()

@client.command(pass_context=True)
async def resume(ctx):
    server_id = ctx.message.server.id
    players[server_id].resume()
    await client.say("**Resuming video..**")

@client.command(pass_context=True)
async def pause(ctx):
    server_id = ctx.message.server.id
    players[server_id].pause()
    await client.say("**Pausing video..**")

@client.command(pass_context=True)
async def stop(ctx):
    server_id = ctx.message.server.id
    players[server_id].stop()
    await client.say("**Stopping video..**")

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

@client.command(pass_context=True)
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]

    await client.say("**Queueing video..**")

client.run(token)