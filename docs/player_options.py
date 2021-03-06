ydl_opts = {
	"format": "bestaudio/best",
	"audio_quality": 0,
	"postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}, {"key": "FFmpegMetadata"}],
	"outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
	"restrictfilenames": True,
	"noplaylist": True,
	"nocheckcertificate": True,
	"ignoreerrors": False,
	"logtostderr": False,
	"quiet": True,
	"no_warnings": True,
	"default_search": "auto",
	"source_address": "0.0.0.0"
}

ffmpeg_options = {"options": "-vn"}

before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
