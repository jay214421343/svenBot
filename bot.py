import discord
import asyncio
import logging
import youtube_dl
from docs import player_options, config
from discord.ext import commands

logging.basicConfig(level=logging.ERROR)
youtube_dl.utils.bug_reports_message = lambda: ""

bot = commands.Bot(command_prefix=config.prefix)


# Collecting media data and creating playable object.
class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.05):
		super().__init__(source, volume)

		self.data = data
		self.title = data.get("title")
		self.url = data.get("url")

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		ytdl = youtube_dl.YoutubeDL(player_options.ydl_opts)
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
		if "entries" in data:
			data = data["entries"][0]
		if stream:
			filename = data["url"]
		else:
			ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **player_options.ffmpeg_options, before_options=player_options.before_args), data=data)


# Contains every function to manipulate the player and playable objects.
class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.media_queue = []
		self.media_name = []
		self.media_volume = []

	# Maybe swap this queue solution for asyncio tuples instead?
	# asyncio.queue(), asyncio.next() etc.
	def check_queue(self, ctx):
		self.media_queue.pop(0)
		self.media_name.pop(0)
		if self.media_queue:
			if self.media_volume:
				self.media_queue[0].volume = self.media_volume[0]
			bot.loop.create_task(ctx.send(f"**Playing queued media:** {self.media_name[0]}"))
			print(f"[Status] Playing queued media: {self.media_name[0]}")
			ctx.voice_client.play(self.media_queue[0], after=lambda e: self.check_queue(ctx))
		else:
			self.media_queue.clear()
			self.media_name.clear()
			self.media_volume.clear()
			bot.loop.create_task(ctx.voice_client.disconnect())
			print(f"[Status] Disconnected, no media in queue..")

	@commands.command()
	async def play(self, ctx, *, url):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send(f"**You are not connected to a voice channel..**")
				raise commands.CommandError("Author not connected to a voice channel..")
		self.source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
		if self.media_queue:
			self.media_queue.append(self.source)
			self.media_name.append(self.source.title)
			print(f"[Status] Queuing: {self.source.title}")
			await ctx.send(f"**Queuing:** {self.source.title}")
		else:
			ctx.voice_client.play(self.source, after=lambda e: self.check_queue(ctx))
			self.media_queue.append(self.source)
			self.media_name.append(self.source.title)
			print(f"[Status] Playing: {self.source.title}")
			await ctx.send(f"**Playing:** {self.source.title}")

	@commands.command()
	async def stop(self, ctx):
		if ctx.voice_client is None:
			return print(f"[Status] Not connected to a voice channel..")
		else:
			await ctx.voice_client.disconnect()
			self.media_queue.clear()
			self.media_name.clear()
			self.media_volume.clear()
			print(f"[Status] Stopped and cleared media queue..")

	@commands.command()
	async def skip(self, ctx):
		if ctx.voice_client is None:
			return print(f"[Status] Not connected to a voice channel..")
		else:
			ctx.voice_client.stop()
			await ctx.send(f"**Skipping media..**")

	@commands.command()
	async def q(self, ctx):
		if not self.media_queue:
			await ctx.send(f"**No queued media..**")
		else:
			await ctx.send(f"**__Current queue__:**")
			for media_num, media in enumerate(self.media_name, start=1):
				await ctx.send(f"{media_num}: {media}")

	@commands.command()
	async def vol(self, ctx, volume: int):
		volume = volume / 100
		if ctx.voice_client is None:
			return await ctx.send("Can't adjust volume, I'm not connected..")
		elif volume > 1.0:
			await ctx.send(f"**You can't go past 100% volume..**")
		elif volume <= 0.0:
			await ctx.send(f"**You can't go below 1% volume..**")
		else:
			self.media_volume.clear()
			ctx.voice_client.source.volume = volume
			self.media_volume.append(volume)
			await ctx.send(f"**Changed volume to:** {int(volume * 100)}%")


@bot.event
async def on_ready():
	print(f"[Status] {bot.user} is now online..")


# Event listener, picking up potential commands tied to the player functions.
# It also cleans up used commands in chat.
@bot.event
async def on_message(message):
	if message.content.startswith("!"):
		await message.delete()
		await bot.process_commands(message)


bot.add_cog(Music(bot))
bot.run(config.discord_bot_token)
