#!/usr/bin/env wpython

import ffmpeg
import os
import pathlib
import re
import sys
import time
import youtube_dl

def cropping(filename):
    print("Processing: ", filename)

    stderr = (ffmpeg
    .input(filename, threads=4)
    .filter("silencedetect", n="-50dB", d=0.5)
    .output("-", format="null")
    .run(capture_stderr=True)[1]
    .decode("utf-8"))

    print("Service file has been made.")

    starts_str = re.findall("silence_start: (\d+.\d+)", stderr)
    ends_str = re.findall("silence_end: (\d+.\d+)", stderr)

    starts = [float(x) for x in starts_str]
    ends = [0] + [float(y) for y in ends_str]

    band_name, _ = [x.strip(" ") for x in filename.split('-')]
    for i, (start, end) in enumerate(zip(ends, starts)):
        res_name = f"{band_name} - {i+1}.mp3"

        kwargs = {
            "ss": start,
            "to": end,
            "threads": 2,
        }

        (ffmpeg
        .input(filename, **kwargs)
        .output(res_name, format="mp3")
        .run_async(quiet=True, overwrite_output=True))

        time.sleep(7) # Prevent full CPU usage

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("links.txt")

    if not os.path.exists('songs'):
        os.mkdir('songs')
    else:
        os.chdir('songs')

    download_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'writedescription': True,
    }

    with youtube_dl.YoutubeDL(download_options) as dl:
        with open('../' + sys.argv[1], 'r') as f:
            for song_url in f:
                dl.download([song_url])

    print("Downloading done, cropping...")
    for song in os.listdir(os.curdir):
        ext = pathlib.Path(song).suffix

        if ext in [".mp4", ".webm"]:
            cropping(song)
