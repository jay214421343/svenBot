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

queue = []
ydl = YoutubeDL()

# Option parameters for youtube_dl.
ydl_opts = {
    "default_search": "auto",
    "format": "bestaudio/best",
    "extractaudio": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "no_warnings": True,
    "verbose": False,
    "skip_download": True
    }

# Checks the queue for media to play.
def check_queue(server):
    queue.pop(0)
    if queue:
        player = queue[0]
        player.start()
        print("[status] Playing queued video..")
    if not queue:
        queue.clear()
        voice_client = client.voice_client_in(server)
        voice_client.loop.create_task(voice_client.disconnect())
        print("[status] Disconnected, no songs in queue..")

@client.event
async def on_ready():
    print("[status] svenBot is now online.")

# Removes the commands from Discord after being executed - clearing up all the clutter.
@client.event
async def on_message(message):
    if message.content.startswith("!"):
        await client.delete_message(message)
    await client.process_commands(message)

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
    player = await voice_client.create_ytdl_player(url, ytdl_options=ydl_opts, after=lambda: check_queue(server))
    player.volume = 0.20
    if queue:
        queue.append(player)
        print("[status] Queuing video..")
        await client.say("**Queuing video..**")
    else:
        queue.append(player)
        player.start()
        print("[status] Playing video..")
        await client.say("**Playing video..**")

@client.command(pass_context=True)
async def vol(ctx, value: int):
    if value > 100:
        await client.say("**Fuck off..**")
    else:
        queue[0].volume = value / 100
        await client.say("**Volume set to:** " + str(value) + "%")

@client.command(pass_context=True)
async def resume(ctx):
    if queue:
        queue[0].resume()
        await client.say("**Resuming video..**")
    else:
        await client.say("**There's nothing to resume..**")

@client.command(pass_context=True)
async def pause(ctx):
    if queue:
        queue[0].pause()
        await client.say("**Pausing video..**")
    else:
        await client.say("**There's nothing to pause..**")

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    queue.clear()
    await voice_client.disconnect()

@client.command(pass_context=True)
async def skip(ctx):
    server = ctx.message.server
    if queue:
        queue[0].pause()
        check_queue(server)
        await client.say("**Skipping video..**")
    else:
        await client.say("**There's nothing to skip..**")

client.run(token)