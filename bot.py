import logging
import config
from weather import Weather, Unit
from discord.ext import commands


# Logs events in the console, does not write to file.
logging.basicConfig(level=logging.DEBUG)

client = commands.Bot(command_prefix="!")

# Lists that keeps track of volume, name and queued songs.
# I was lazy with this one, will change all of this into a dictionary instead.
song_queue = []
song_name = []
song_volume = []


# Initializes bot and prints out if the bot is ready/online.
@client.event
async def on_ready():
    print(f"[status] svenBot is now online.")


# Removes the commands from Discord after being executed.
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
        client.loop.create_task(client.send_message(ctx.message.channel, f"**P \
            laying queued video:** {song_name[0]}"))
        print(f"[status] Playing queued video: {song_name[0]}")
        song_queue[0].start()
    else:
        server = ctx.message.server
        song_queue.clear()
        song_name.clear()
        song_volume.clear()
        voice_client = client.voice_client_in(server)
        voice_client.loop.create_task(voice_client.disconnect())
        print(f"[status] Disconnected, no songs in queue")


# Will summon the bot and play or queue media.
@client.command(pass_context=True)
async def play(ctx, *, url):
    if "/playlist" in url:
        await client.say(f"You can't queue playlists")
    else:
        server = ctx.message.server
        if client.is_voice_connected(server):
            voice_client = client.voice_client_in(server)
        else:
            channel = ctx.message.author.voice.voice_channel
            await client.join_voice_channel(channel)
            voice_client = client.voice_client_in(server)
        player = await voice_client.create_ytdl_player(url,
                                                       ytdl_options=config.ydl_opts,
                                                       after=lambda: check_queue(ctx),
                                                       before_options=config.before_args)
        player.volume = 0.10
        if song_queue:
            song_queue.append(player)
            song_name.append(player.title)
            print(f"[status] Queuing: {player.title}")
            await client.say(f"**Queuing video**")
        else:
            song_queue.append(player)
            song_name.append(player.title)
            player.start()
            song_volume.append(song_queue[0].volume)
            print(f"[status] Playing: {player.title}")
            await client.say(f"**Playing:** {player.title}")


# Outputs the current queue.
@client.command(pass_context=True)
async def queue(ctx):
    await client.say(f"__**CURRENT QUEUE__:**")
    for number, song in enumerate(song_name, 1):
        await client.say(f"{number}: {song}")


# Volume control, will either change volume or display current volume.
@client.command(pass_context=True)
async def vol(ctx, *args, **kwargs):
    if song_queue:
        if not args:
            await client.say(f"**Current volume:** \
                             {int(song_volume[0] * 100)}%")
        elif int(args[0]) > 100:
            await client.say("**Can't go higher than 100% volume**")
        elif int(args[0]) <= 100:
            song_volume.clear()
            song_queue[0].volume = int(args[0]) / 100
            song_volume.append(song_queue[0].volume)
            await client.say(f"**Volume set to:** {str(args[0])}%")
    else:
        await client.say(f"**There's nothing playing, can't adjust volume**")


# Resumes paused player.
@client.command(pass_context=True)
async def resume(ctx):
    if song_queue:
        song_queue[0].resume()
        await client.say(f"**Resuming video**")
    else:
        await client.say(f"**There's nothing to resume**")


# Pauses player.
@client.command(pass_context=True)
async def pause(ctx):
    if song_queue:
        song_queue[0].pause()
        await client.say(f"**Pausing video**")
    else:
        await client.say(f"**There's nothing to pause**")


# Makes bot leave the current voice channel.
@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    if client.voice_client_in(server):
        voice_client = client.voice_client_in(server)
        song_queue.clear()
        song_name.clear()
        song_volume.clear()
        await voice_client.disconnect()
        print(f"[status] Cleared queue and disconnected")
    else:
        await client.say(f"**Can't leave if I'm not in a voice channel**")


# Skips current song to the next song in queue.
@client.command(pass_context=True)
async def skip(ctx):
    if song_queue:
        song_queue[0].pause()
        check_queue(ctx)
        await client.say(f"**Skipping video**")
    else:
        await client.say(f"**There's nothing to skip**")


# Outputs current weather in given area.
@client.command(pass_context=True)
async def weather(ctx, *, place):
    weather_unit = Weather(unit=Unit.CELSIUS)
    location = weather_unit.lookup_by_location(place)
    condition = location.condition
    await client.say(f"**Current weather in {place}:** \
                     {condition.temp}°C and {condition.text}")


# Outputs a two week forecast in given area.
@client.command(pass_context=True)
async def forecast(ctx, *, place):
    weather_unit = Weather(unit=Unit.CELSIUS)
    location = weather_unit.lookup_by_location(place)
    forecasts = location.forecast
    await client.say(f"**Forecast for {place}:** ")
    for forecast in forecasts:
        await client.say(f"**{forecast.day}:** {forecast.text}, with a high \
                         of {forecast.high}°C and a low of {forecast.low}°C")


# Outputs a list of available bot commands.
@client.command(pass_context=True)
async def botcommands(ctx):
    botcommands_list = [
        "__**Available commands for svenBot**__",
        "**!play:** Plays/queues video, use URL or search string.",
        "**!skip:** Skips current song.",
        "**!resume:** Resumes a paused song.",
        "**!pause:** Pauses current song.",
        "**!leave:** Clears queue and leaves voice channel.",
        "**!queue:** Outputs the current queue of songs.",
        "**!vol:** Adjust volume using value between 1-100 (no value will \
        output current volume).",
        "**!weather:** Input a city name to get weather info.",
        "**!forecast:** Input a city name to get forecast info."
    ]
    await client.say(f"\n".join(botcommands_list))

client.run(config.token)
