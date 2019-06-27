#!/usr/bin/env wpython

import argparse
import ffmpeg
import os
import pathlib
import re
import sys
import time
import youtube_dl

def init_argparse():
    parser = argparse.ArgumentParser(description="Download your favourite albums from YouTube.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-l", "--link", help="Link to album on YouTube")
    group.add_argument("-f", "--filename", help="File with YouTube links")

    parser.add_argument("-o", "--out", default="songs", help="Output folder (default: songs)")

    return parser

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
    parser = init_argparse()
    args = vars(parser.parse_args(args=None if sys.argv[1:] else ["-h"]))

    link, filename, outdir = args["link"], args["filename"], args["out"]

    if filename and os.path.exists(filename):
        with open(filename, "r") as file:
            links = [line.rstrip("\n") for line in file.readlines()]

    elif link:
        links = [link]

    try_chdir_except_create(outdir)
    download_from_youtube(links)

    for filename in os.listdir(os.curdir):
        ext = pathlib.Path(filename).suffix

        if ext in [".mp4", ".webm"]:
            starts, ends = get_silence_intervals(filename)
            crop_album_to_songs(filename, starts, ends)
