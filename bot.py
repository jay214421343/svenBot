import discord
import logging
import youtube_dl
import asyncio
from youtube_dl import YoutubeDL
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
ydl = YoutubeDL()

youtube_dl_opts = {
    "default_search": "auto",
    "format": "bestaudio/best",
    "extractaudio": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "no_warnings": True,
    "verbose": False
    }

def check_queue(id_):
    if len(queues[id_.id]) != 0:
        player = queues[id_.id].pop(0)
        players[id_.id] = player
        player.start()
    else:
        print("Automatically disconnected, no songs in the queue.")
        server = id_
        voice_client = client.voice_client_in(server)
        voice_client.loop.create_task(voice_client.disconnect())

@client.event
async def on_ready():
    print("svenBot is now online.")

# Removes the commands from Discord after being executed - clearing up all the clutter.
@client.event
async def on_message(message):
    if message.content.startswith("!"):
        await client.delete_message(message)
    await client.process_commands(message)

@client.command(pass_context=True)
async def vol(ctx, value: int):
    if value > 100:
        await client.say("**Fuck off..**")
    else:
        server_id = ctx.message.server.id
        players[server_id].volume = value / 100
        await client.say("**Volume set to:** " + str(value) + "%")

# Will summon the bot and play or queue media.
@client.command(pass_context=True)
async def play(ctx, *, url):
    server = ctx.message.server
    if client.is_voice_connected(server) is True:
        voice_client = client.voice_client_in(server)
        player = await voice_client.create_ytdl_player(url, ytdl_options=youtube_dl_opts, after=lambda: check_queue(server))
        player.volume = 0.15
        players[server.id] = player
        if server.id in queues:
            queues[server.id].append(player)
        else:
            queues[server.id] = [player]
        await client.say("**Queueing video..**")
    elif client.is_voice_connected(server) is False:
        channel = ctx.message.author.voice.voice_channel
        await client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
        player = await voice_client.create_ytdl_player(url, ytdl_options=youtube_dl_opts, after=lambda: check_queue(server))
        player.volume = 0.15
        players[server.id] = player
        player.start()
        await client.say("**Playing video..**")
    else:
        await client.say("**You probably didn't do that right, try again..**")

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
async def skip(ctx):
    server_id = ctx.message.server.id
    players[server_id].stop()
    server = ctx.message.server
    check_queue(server.id)
    await client.say("**Skipping video..**")

client.run(token)