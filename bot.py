import discord
import asyncio
import logging
import youtube_dl
from docs import player_options, config
from discord.ext import commands

logging.basicConfig(level=logging.ERROR)
youtube_dl.utils.bug_reports_message = lambda: ""

bot = commands.Bot(command_prefix=config.prefix)

media_queue = [] 	# Stores playable media object.
media_name = []  	# Stores media titles in the order of playable objects.
media_volume = []	# Stores set volume of choice, so that it carries over to next played media.
media_data = None # Stores media title/data temporarily before pushing it to media_name.

async def from_url(ctx, url, *, loop=None, stream=False):
	global media_data
	ytdl = youtube_dl.YoutubeDL(player_options.ydl_opts)
	loop = loop or asyncio.get_event_loop()
	data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
	if "entries" in data:
		data = data["entries"][0]
	if stream:
		filename = data["url"]
	else:
		ytdl.prepare_filename(data)
	media_data = data['title']
	return discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **player_options.ffmpeg_options, before_options=player_options.before_args))

# self.url = data.get("url")
# Maybe swap this queue solution for asyncio tuples instead?
# asyncio.queue(), asyncio.next() etc.
def check_queue(ctx):
	media_queue.pop(0)
	media_name.pop(0)
	if media_queue:
		if media_volume:
			media_queue[0].volume = media_volume[0]
		bot.loop.create_task(ctx.send(f"**Playing queued media:** {media_name[0]}"))
		print(f"[Status] Playing queued media: {media_name[0]}")
		ctx.voice_client.play(media_queue[0], after=lambda e: check_queue(ctx))
	else:
		media_queue.clear()
		media_name.clear()
		media_volume.clear()
		bot.loop.create_task(ctx.voice_client.disconnect())
		print(f"[Status] Disconnected, no media in queue..")

@bot.command(pass_context=True)
async def play(ctx, *, url):
	if ctx.voice_client is None:
		if ctx.author.voice:
			await ctx.author.voice.channel.connect()
		else:
			await ctx.send(f"**You are not connected to a voice channel..**")
			raise commands.CommandError("Author not connected to a voice channel..")
	source = await from_url(ctx, url, loop=bot.loop, stream=True)
	source.volume = 0.1
	if media_queue:
		media_queue.append(source)
		media_name.append(media_data)
		print(f"[Status] Queuing: {media_data}")
		await ctx.send(f"**Queuing:** {media_data}")
	else:
		ctx.voice_client.play(source, after=lambda e: check_queue(ctx))
		media_queue.append(source)
		media_name.append(media_data)
		print(f"[Status] Playing: {media_data}")
		await ctx.send(f"**Playing:** {media_data}")

@bot.command(pass_context=True)
async def stop(ctx):
	if ctx.voice_client is None:
		return print(f"[Status] Not connected to a voice channel..")
	else:
		media_name.clear()
		media_queue.clear()
		media_volume.clear()
		await ctx.voice_client.disconnect()
		print(f"[Status] Stopped and cleared media queue..")

@bot.command(pass_context=True)
async def skip(ctx):
	if ctx.voice_client is None:
		return print(f"[Status] Not connected to a voice channel..")
	else:
		ctx.voice_client.stop()
		await ctx.send(f"**Skipping media..**")

@bot.command(pass_context=True)
async def q(ctx):
	if not media_queue:
		await ctx.send(f"**No queued media..**")
	else:
		await ctx.send(f"**__Current queue__:**")
		for media_num, media in enumerate(media_name, start=1):
			await ctx.send(f"{media_num}: {media}")

@bot.command(pass_context=True)
async def vol(ctx, volume: int):
	volume = volume / 100
	if ctx.voice_client is None:
		return await ctx.send("Can't adjust volume, I'm not connected..")
	elif volume > 1.0:
		await ctx.send(f"**You can't go past 100% volume..**")
	elif volume <= 0.0:
		await ctx.send(f"**You can't go below 1% volume..**")
	else:
		media_volume.clear()
		ctx.voice_client.source.volume = volume
		media_volume.append(volume)
		await ctx.send(f"**Changed volume to:** {int(volume * 100)}%")

@bot.event
async def on_ready():
	print(f"[Status] {bot.user} is now online..")

# Event listener, listening for commands.
# It also cleans up used commands in chat.
@bot.event
async def on_message(message):
	if message.content.startswith("!"):
		await message.delete()
	await bot.process_commands(message)

bot.run(config.discord_bot_token)