# svenBot

svenBot is a **simple/lightweight** music bot for Discord, made with **Python 3.6**.
It is currently under heavy development, many features still to be added, 
but it will still remain a fairly simple and lightweight music bot.

## Commands
| Commands          | Description                                |
| ----------------- | ------------------------------------------ |
| !play             | [YouTube URL/String] (also works as queue) |
| !skip             | Skips current song                         |
| !resume           | Resumes a paused song                      |
| !pause            | Pauses current song                        |
| !leave            | Clears queue and leaves voice channel      |
| !vol              | [Value between 1-100]                      |

## Acknowledged issues and bugs that I'm currently working on
- [x] Volume control and adding a volume value limitation
- [x] Being able to skip a song using !skip
- [x] Being able to queue properly with !play (replacing !queue)
- [x] Bot to leave voice channel if nothing is playing
- [ ] Extract video information when using search string and not URL