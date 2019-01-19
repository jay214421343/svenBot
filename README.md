# svenBot
svenBot is a **simple/lightweight** non-guild music bot for Discord, made with **Python 3.6**. 
This bot is built for private hosting, custom use.

## Installation
Clone this repo.
```
$ git clone https://github.com/caene/svenBot.git
```

Install required Python libraries (using requirements.txt that comes with this repo).
```
$ pip install -r requirements.txt
```
**Important:** This bot also requires the host to have ffmpeg and libopus installed on the system.
You should use this bot with ffmpeg 3.4+. Should be simple enough to figure out.

## Configure
Now it's time to configure `config.py`. Go to https://discordapp.com/developers/applications/ 
and create an application, name the application/bot whatever you want. When you have 
created the application, you should be able to see the "client secret" aka bot token by clicking 
"Click to reveal". Copy that token into the `config.py` file. 

## Run
Run bot.py using Python 3.6, Python alias may vary.
```
$ python bot.py
```

## Commands
| Commands          | Description                                                                       |
| ----------------- | --------------------------------------------------------------------------------- |
| !play             | Plays/queues video, use URL or search string.                                     |
| !skip             | Skips current song.                                                               |
| !resume           | Resumes a paused song.                                                            |
| !pause            | Pauses current song.                                                              |
| !leave            | Clears queue and leaves voice channel.                                            |
| !queue            | Outputs out the current queue of songs.                                           |
| !vol              | Adjust volume using value between 1-100 (no value will output current volume).    |
| !weather          | Checks the current weather for given location.                                    |
| !forecast         | Checks the forecast for the coming two weeks.                                     |
| !botcommands      | Outputs all the bot features.                                                     |
