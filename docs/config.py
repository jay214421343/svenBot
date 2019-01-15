# Discord bot token
token = "DISCORD BOT TOKEN HERE"

# Added options for the YouTube Donwloader, telling it how to handle the downloaded/streamed media
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

# Arguments added to the YouTube Downloader/player, basically giving the player some time to catch up and reconnect to the media
before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"