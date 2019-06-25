from __future__ import unicode_literals
import youtube_dl
import sys
import os
import re
from sys import argv

if len(argv) == 1:
    print(("Create a txt file in the same folder"
        "with YT links to videos and pass as arg."))
    sys.exit(0)

# Download data and config
download_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'nocheckcertificate': True,
    'writedescription': True,
}

# Directory
if not os.path.exists('songs'):
    os.mkdir('songs')
else:
    os.chdir('songs')

# Download
with youtube_dl.YoutubeDL(download_options) as dl:
    with open('../' + argv[1], 'r') as f:
        for song_url in f:
         dl.download([song_url])

#Per each file
def cropping(filename):
    #deleting the file extension
    no_extension = filename.split('.')
    no_extension = no_extension[0]

    band_title = filename.split('-')[0]

    print("Processing: ", no_extension)

    #getting the songs' titles
    #with open(no_extension + '.description', 'rt') as description:
        #strdesc = description.read()
        #gr = re.findall(r"d+:\d+", strdesc)

    #titles = []

    #print(gr)

    #for a in titlelines:
        #titles.append((gr[0]))

    #generating a txt file with silence parts
    os.system(f"ffmpeg -i \"{filename}\" -af silencedetect=noise=-40dB:d=0.5 -f null - 2> vol.txt -threads 4")
    print("Service file has been made.")

    with open ('vol.txt', 'rt') as myfile:
        strfile = myfile.read()
        gr1 = re.findall(r"silence_end: \d+.\d+", strfile)
        gr2 = re.findall(r"silence_start: \d+.\d+", strfile)
        print(strfile)

    ends = []
    begs = []

    print(ends)

    #get numbers from substrings
    for a in gr1:
        gr = re.findall("\d+\.\d+", a)
        begs.append(float(gr[0]))

    for a in gr2:
        gr = re.findall("\d+\.\d+", a)
        ends.append(float(gr[0]))

    #begs and ends lens are equal
    for i in range(len(begs)):
        silence_end = ends[i]
        silence_beg = begs[i]

        if i != 0:
            beg_diff = (silence_beg - ends[i - 1]) / 2
        else:
            silence_beg = 0
            beg_diff = 0

        if i < len(begs) - 1:
            end_diff = (begs[i+1] - silence_end) / 2
        else:
            end_diff = 0

        ffmpeg_arg = ("ffmpeg -loglevel quiet -ss {2}"
                      "-i \"{0}\" -to {3} \"{1}.mp3\" -threads 4")

        ffmpeg_arg = ffmpeg_arg.format(
           filename,
           i,
           silence_beg,
           silence_end - silence_beg)

        os.system(ffmpeg_arg)

# Crop
print("Downloading done, cropping...")
for song in os.listdir(os.curdir):
    if (song.split('.')[-1] == 'webm'
        or song.split('.')[-1] == 'mp4'):

        cropping(song)
