#!/usr/bin/env wpython

import ffmpeg
import os
import pathlib
import re
import sys
import youtube_dl

def cropping(filename):
    print("Processing: ", filename)

    command = f'ffmpeg \
                -i "{filename}" \
                -af silencedetect=noise=-50dB:d=0.5 \
                -f null - 2> vol.txt \
                -threads 4'

    os.system(command)

    print("Service file has been made.")

    with open ("vol.txt", "rt") as file:
        file_content = file.read()

        starts_str = re.findall("silence_start: (\d+.\d+)", file_content)
        ends_str = re.findall("silence_end: (\d+.\d+)", file_content)

    starts = [float(x) for x in starts_str]
    ends = [0] + [float(y) for y in ends_str]

    band_name, _ = [x.strip(" ") for x in filename.split('-')]
    for i, (start, end) in enumerate(zip(ends, starts)):
        res_name = f"{band_name} - {i+1}"

        command = f'ffmpeg \
                    -loglevel quiet \
                    -threads 4 \
                    -ss {start} \
                    -i "{filename}" \
                    -to {end} \
                    "{res_name}.mp3"'

        os.system(command)

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
