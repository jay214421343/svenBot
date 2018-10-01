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

def check_queue(server):
    player = queues[server.id].pop(0)
    if queues[server.id]:
        player = queues[server.id][0]
        player.start()
        print("Playing queued video..")
    if not queues[server.id]:
        print("Automatically disconnected, no songs in the queue.")
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
        server = ctx.message.server
        queues[server.id].volume = value / 100
        await client.say("**Volume set to:** " + str(value) + "%")

# Will summon the bot and play or queue media.
@client.command(pass_context=True)
async def play(ctx, *, url):
    server = ctx.message.server
    if client.is_voice_connected(server):
        voice_client = client.voice_client_in(server)
    elif not client.is_voice_connected(server):
        channel = ctx.message.author.voice.voice_channel
        await client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
    else:
        await client.say("**You probably didn't do that right, try again..**")
    player = await voice_client.create_ytdl_player(url, ytdl_options=youtube_dl_opts, after=lambda: check_queue(server))
    player.volume = 0.15
    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
        player.start()
        print("Playing video..")
    await client.say("**Playing video..**")

@client.command(pass_context=True)
async def resume(ctx):
    server = ctx.message.server
    if queues[server.id]:
        queues[server.id][0].resume()
        await client.say("**Resuming video..**")
    else:
        await client.say("**There's nothing to resume..**")

@client.command(pass_context=True)
async def pause(ctx):
    server = ctx.message.server
    if queues[server.id]:
        queues[server.id][0].pause()
        await client.say("**Pausing video..**")
    else:
        await client.say("**There's nothing to pause..**")

@client.command(pass_context=True)
async def stop(ctx):
    server = ctx.message.server
    if queues[server.id]:
        queues[server.id][0].stop()
        await client.say("**Stopping video..**")
    else:
        await client.say("**There's nothing to stop..**")

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()
    queues[server.id] = []

@client.command(pass_context=True)
async def skip(ctx):
    server = ctx.message.server
    queues[server.id][0].stop()
    check_queue(server.id)
    await client.say("**Skipping video..**")

client.run(token)