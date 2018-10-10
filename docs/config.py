token = "INSERT YOUR BOT TOKEN RIGHT HERE"

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