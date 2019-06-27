# YouTube Music Snatcher

Simple script to help you downloading music albums from YouTube and separate them into mp3 tracks.

# Dependencies

This project uses Python3 and some external modules. You can intstall them by running

```
pip install --no-cache-dir -r requirements.txt
```

# Usage

```
usage: main.py [-h] (-l LINK | -f FILENAME) [-o OUT]

Download your favourite albums from YouTube.

optional arguments:
  -h, --help            show this help message and exit
  -l LINK, --link LINK  Link to album on YouTube
  -f FILENAME, --filename FILENAME
                        File with YouTube links
  -o OUT, --out OUT     Output folder (default: songs)
```

Example: ```python main.py -l https://youtu.be/zdQp9OEhRrc```
