# Discord bot token
token = "NDMzNzA0MzUwODIxNTE1Mjc0.DypuTg.PRWhHtn7CuJ7xJikDA1mTEekjRA"

# Added options for the YouTube Donwloader.
ydl_opts = {
    "default_search": "auto",
    "format": "bestaudio/best",
    "postprocessors": [{'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'},
                       {'key': 'FFmpegMetadata'}],
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

# Giving player/downloader time to reconnect to streamed media.
before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"