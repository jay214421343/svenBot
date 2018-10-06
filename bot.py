import discord
import logging
import youtube_dl
import asyncio
from youtube_dl import YoutubeDL
from discord.ext import commands
from docs.config import token

client = commands.Bot(command_prefix = "!")
client.remove_command("help")

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

song_queue = []
song_name = []
song_volume = []

# Option parameters for youtube_dl.
ydl_opts = {
    "default_search": "auto",
    "format": "bestaudio/best",
    "postprocessors": [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}, {'key': 'FFmpegMetadata'}],
    "extractaudio": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "no_warnings": True,
    "verbose": False,
    "quiet": True,
    "forcetitle": True,
    "forceurl": True,
    "skip_download": True,
    "noplaylist": True
    }

ydl = YoutubeDL()

@client.event
async def on_ready():
    print("[status] svenBot is now online.")

# Removes the commands from Discord after being executed - clearing up all the clutter.
@client.event
async def on_message(message):
    if message.content.startswith("!"):
        await client.delete_message(message)
    await client.process_commands(message)

@client.command(pass_context=True)
async def help(ctx):
    help_list = [
        "__**Available commands for svenBot**__",
        "**!play:** Plays/queues video, use URL or search string",
        "**!skip:** Skips current song",
        "**!resume:** Resumes a paused song",
        "**!pause:** Pauses current song",
        "**!leave:** Clears queue and leaves voice channel",
        "**!queue:** Prints out the current queue of songs",
        "**!vol:** Adjust volume using value between 1-100"
    ]
    await client.say("\n".join(help_list))

# Checks the queue for media to play.
def check_queue(ctx):
    server = ctx.message.server
    song_queue.pop(0)
    song_name.pop(0)
    if song_queue:
        if song_volume:
            song_queue[0].volume = song_volume[0]
        song_queue[0].start()
        client.loop.create_task(client.say(f"**Playing queued video:** {song_name[0]}"))
        print(f"[status] Playing queued video: {song_name[0]}")
    if not song_queue:
        song_queue.clear()
        song_name.clear()
        song_volume.clear()
        voice_client = client.voice_client_in(server)
        voice_client.loop.create_task(voice_client.disconnect())
        print("[status] Disconnected, no songs in queue..")

# Will summon the bot and play or queue media.
@client.command(pass_context=True)
async def play(ctx, *, url):
    server = ctx.message.server
    if "/playlist" in url:
        await client.say("You can't queue playlists..")
    else:
        if client.is_voice_connected(server):
            voice_client = client.voice_client_in(server)
        elif not client.is_voice_connected(server):
            channel = ctx.message.author.voice.voice_channel
            await client.join_voice_channel(channel)
            voice_client = client.voice_client_in(server)
        else:
            await client.say("**You probably didn't do that right, try again..**")
        player = await voice_client.create_ytdl_player(url, ytdl_options=ydl_opts, after=lambda: check_queue(ctx))
        player.volume = 0.10
        if song_queue:
            song_queue.append(player)
            song_name.append(player.title)
            print(f"[status] Queuing: {player.title}")
            await client.say("**Queuing video..**")
        else:
            song_queue.append(player)
            song_name.append(player.title)
            player.start()
            print(f"[status] Playing: {player.title}")
            await client.say(f"**Playing:** {player.title}")

@client.command(pass_context=True)
async def queue(ctx):
    await client.say("__**CURRENT QUEUE:**__")
    for number, song in enumerate(song_name, 1):
        await client.say("%d: %s" % (number, song))

@client.command(pass_context=True)
async def vol(ctx, value: int):
    if value > 100:
        await client.say("**Fuck off..**")
    else:
        song_volume.clear()
        song_queue[0].volume = value / 100
        song_volume.append(song_queue[0].volume)
        await client.say(f"**Volume set to:** {song_volume[0]}%")

@client.command(pass_context=True)
async def resume(ctx):
    if song_queue:
        song_queue[0].resume()
        await client.say("**Resuming video..**")
    else:
        await client.say("**There's nothing to resume..**")

@client.command(pass_context=True)
async def pause(ctx):
    if song_queue:
        song_queue[0].pause()
        await client.say("**Pausing video..**")
    else:
        await client.say("**There's nothing to pause..**")

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    song_queue.clear()
    song_name.clear()
    await voice_client.disconnect()
    print("[status] Cleared queue and disconnected..")

@client.command(pass_context=True)
async def skip(ctx):
    if song_queue:
        song_queue[0].pause()
        check_queue(ctx)
        await client.say("**Skipping video..**")
    else:
        await client.say("**There's nothing to skip..**")

client.run(token)