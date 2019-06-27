#!/usr/bin/env wpython

import ffmpeg
import os
import pathlib
import re
import time
import youtube_dl


def try_chdir_except_create(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    os.chdir(dirname)


def download_from_youtube(links):
    download_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'writedescription': True,
    }

    with youtube_dl.YoutubeDL(download_options) as dl:
        dl.download(links)


def get_silence_intervals(filename):
    stderr = (ffmpeg
        .input(filename, threads=4)
        .filter("silencedetect", n="-50dB", d=0.5)
        .output("-", format="null")
        .run(capture_stderr=True)[1]
        .decode("utf-8")
    )

    starts_str = re.findall("silence_start: (\d+.\d+)", stderr)
    ends_str   = re.findall("silence_end: (\d+.\d+)", stderr)

    starts = [float(x) for x in starts_str]
    ends = [0] + [float(y) for y in ends_str]

    return (starts, ends)


def crop_album_to_songs(filename, silence_starts, silence_ends):
    band_name = filename.split('-')[0].strip(" ")

    songs_intervals = zip(silence_ends, silence_starts)
    for i, (song_start, sond_end) in enumerate(songs_intervals):
        ouptut_filename = f"{band_name} - {i+1}.mp3"

        kwargs = {
            "ss": song_start,
            "to": sond_end,
            "threads": 2,
        }

        (ffmpeg
        .input(filename, **kwargs)
        .output(ouptut_filename, format="mp3")
        .run_async(quiet=True, overwrite_output=True))

        time.sleep(7) # Prevent full CPU usage


if __name__ == "__main__":
    if os.path.exists("links.txt"):
        with open("links.txt", "r") as file:
            links = [line.rstrip("\n") for line in file.readlines()]

            try_chdir_except_create("songs")
            download_from_youtube(links)

    for filename in os.listdir(os.curdir):
        ext = pathlib.Path(filename).suffix

        if ext in [".mp4", ".webm"]:
            starts, ends = get_silence_intervals(filename)
            crop_album_to_songs(filename, starts, ends)
