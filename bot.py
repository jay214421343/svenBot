import discord
import logging
import youtube_dl
import docs.config
from weather import Weather, Unit
from youtube_dl import YoutubeDL
from discord.ext import commands

logging.basicConfig(level=logging.DEBUG)

client = commands.Bot(command_prefix = "!")
client.remove_command("help")

song_queue = []
song_name = []
song_volume = []

# Initializes bot and prints out if the bot is ready/online
@client.event
async def on_ready():
    print("[status] svenBot is now online.")

# Removes the commands from Discord after being executed - clearing up all the clutter.
@client.event
async def on_message(message):
    if message.content.startswith("!"):
        await client.delete_message(message)
    await client.process_commands(message)

# Checks the queue for media to play.
def check_queue(ctx):
    song_queue.pop(0)
    song_name.pop(0)
    if song_queue:
        if song_volume:
            song_queue[0].volume = song_volume[0]
        client.loop.create_task(client.send_message(ctx.message.channel, f"**Playing queued video:** {song_name[0]}"))
        print(f"[status] Playing queued video: {song_name[0]}")
        song_queue[0].start()
    elif not song_queue:
        server = ctx.message.server
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
        player = await voice_client.create_ytdl_player(url, ytdl_options=docs.config.ydl_opts, after=lambda: check_queue(ctx), before_options=docs.config.before_args)
        player.volume = 0.10
        if song_queue:
            song_queue.append(player)
            song_name.append(player.title)
            print(f"[status] Queuing: {player.title}")
            await client.say("**Queuing video..**")
        elif not song_queue:
            song_queue.append(player)
            song_name.append(player.title)
            player.start()
            song_volume.append(song_queue[0].volume)
            print(f"[status] Playing: {player.title}")
            await client.say(f"**Playing:** {player.title}")

# Outputs the current queue
@client.command(pass_context=True)
async def queue(ctx):
    await client.say("__**CURRENT QUEUE:**__")
    for number, song in enumerate(song_name, 1):
        await client.say("%d: %s" % (number, song))

# Volume control
@client.command(pass_context=True)
async def vol(ctx, value: int):
    if song_queue:
        if value > 100:
            await client.say("**Can't go higher than 100% volume..**")
        else:
            song_volume.clear()
            song_queue[0].volume = value / 100
            song_volume.append(song_queue[0].volume)
            await client.say(f"**Volume set to:** {str(value)}%")
    elif not song_queue:
        await client.say("**There's nothing playing, can't adjust volume..**")

# Display current volume
@client.command(pass_context=True)
async def currentvol(ctx):
    if song_queue:
        await client.say(f"**Current volume:** {str(int(song_volume[0] * 100))}%")
    elif not song_queue:
        await client.say("**There's nothing playing, no current volume..**")

# Resumes paused player
@client.command(pass_context=True)
async def resume(ctx):
    if song_queue:
        song_queue[0].resume()
        await client.say("**Resuming video..**")
    elif not song_queue:
        await client.say("**There's nothing to resume..**")

# Pauses player
@client.command(pass_context=True)
async def pause(ctx):
    if song_queue:
        song_queue[0].pause()
        await client.say("**Pausing video..**")
    elif not song_queue:
        await client.say("**There's nothing to pause..**")

# Makes bot leave the current voice channel
@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    if client.voice_client_in(server):
        voice_client = client.voice_client_in(server)
        song_queue.clear()
        song_name.clear()
        song_volume.clear()
        await voice_client.disconnect()
        print("[status] Cleared queue and disconnected..")
    elif not client.voice_client_in(server):
        await client.say("**Can't leave if I'm not in a voice channel..**")

# Skips current song to the next song in queue
@client.command(pass_context=True)
async def skip(ctx):
    if song_queue:
        song_queue[0].pause()
        check_queue(ctx)
        await client.say("**Skipping video..**")
    elif not song_queue:
        await client.say("**There's nothing to skip..**")

# Outputs current weather in given area
@client.command(pass_context=True)
async def weather(ctx, *, place):
    weather_unit = Weather(unit=Unit.CELSIUS)
    location = weather_unit.lookup_by_location(place)
    condition = location.condition
    await client.say(f"**Current weather in {place}:** {condition.temp}°C and {condition.text}..")

# Outputs a two week forecast in given area
@client.command(pass_context=True)
async def forecast(ctx, *, place):
    weather_unit = Weather(unit=Unit.CELSIUS)
    location = weather_unit.lookup_by_location(place)
    forecasts = location.forecast
    await client.say(f"**Forecast for {place}:** ")
    for forecast in forecasts:
        await client.say(f"**{forecast.day}:** {forecast.text}, with a high of {forecast.high}°C and a low of {forecast.low}°C..")

# Outputs a list of available bot commands
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
        "**!vol:** Adjust volume using value between 1-100",
        "**!currentvol:** Displays current volume",
        "**!weather:** Input a city name to get weather info",
        "**!forecast:** Input a city name to get forecast info"
    ]
    await client.say("\n".join(help_list))

client.run(docs.config.token)