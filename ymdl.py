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
    os.system(("ffmpeg -i \"{0}\" -af silencedetect=noise=-50dB:d=0.5"
        " -f null - 2> vol.txt -threads 4".format(filename)))

    print("Service file has been made.")

    with open ('vol.txt', 'rt') as myfile:
        strfile = myfile.read()
        gr1 = re.findall(r"silence_end: \d+.\d+", strfile)
        gr2 = re.findall(r"silence_start: \d+.\d+", strfile)
   
    begs = []
    ends = []

    #get numbers from substrings
    for a in gr1:
        gr = re.findall("\d+\.\d+", a)
        begs.append(float(gr[0]))

    for a in gr2:
        gr = re.findall("\d+\.\d+", a)
        ends.append(float(gr[0]))

    #this can happen if no silence in the very beginning of the track
    if len(ends) != len(begs):
        begs = [0] + begs

    #begs and ends lens are or now are equal if wasn't
    for i in range(len(ends)):
        begin_cut = begs[i]
        end_cut = ends[i]

        if i != 0:
            beg_diff = (begin_cut - ends[i - 1]) / 2
        else:
            begin_cut = 0
            beg_diff = 0

        if i < len(begs) - 1:
            end_diff = (begs[i+1] - end_cut) / 2
        else:
            end_diff = 0

        ffmpeg_arg = ("ffmpeg -loglevel quiet -ss {2}"
                      " -i \"{0}\" -to {3} \"{1}.mp3\" -threads 4")

        ffmpeg_arg = ffmpeg_arg.format(
           filename,
           band_title + "- " + str(i),
           begin_cut,
           end_cut - begin_cut)

        os.system(ffmpeg_arg)

# Crop
print("Downloading done, cropping...")
for song in os.listdir(os.curdir):
    if (song.split('.')[-1] == 'webm'
        or song.split('.')[-1] == 'mp4'):

        cropping(song)
