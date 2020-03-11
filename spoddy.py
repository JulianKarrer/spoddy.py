import argparse
import urllib.request
import re
import subprocess
import os
import threading
from concurrent.futures import ThreadPoolExecutor

#GLOBAL VARIABLES
playlistTitle = "playlist"
playlistTracks = []
playlistArtists = []
searchKeywords = " Lyrics Official"

#catch args passed to the python script and provide help info
parser = argparse.ArgumentParser(description='Search for and download entire Spotify playlists from Youtube')
parser.add_argument("url",nargs=1,help="The url of the Spotify playlist to be downloaded") #required, positional
parser.add_argument("--pathToYoutube-dl",default="youtube-dl",help="""The path to the youtube-dl. Defaults to "youtube-dl". When using Windows, this should point to the youtube-dl.exe file if it is not in spoddy.py's root directory. When using UNIX there is no need to change this.""")
parser.add_argument("--fast",action='store_true',help="When this flag is set, instead of downloading the songs as videos from youtube, then converting them with ffmpeg, the m4a audio is directly downloaded if present. this can significantly speed up the download process. Use if ffmpeg is not available.")
parser.add_argument("--mp3",action='store_true',help="When using --fast also set this flag to convert all m4a songs to mp3 after downloading them using ffmpeg. This requires ffmpeg in the working directory (Windows) or a valid ffmpeg installation (UNIX).")
parser.add_argument("--threads", type=int, default=7, nargs=r"?", help="This specifies the maximum number of threads to use when downloading and converting songs. Defaults to 7.")
args = parser.parse_args()


#use args to set values
pathToYoutubedl = "youtube-dl"
if (args.pathToYoutube_dl!="youtube-dl"):
	pathToYoutubedl = args.pathToYoutube_dl

command = pathToYoutubedl + " -x --audio-format mp3 --audio-quality 0 "
if(args.fast):
	command = pathToYoutubedl + " -f bestaudio[ext=m4a] "

maxThreads = 7	
if (args.threads != 7):
	maxThreads = args.threads



#SCRAPE SPOTIFY TRACK NAMES AND ARTISTS
try:
	#get the webpage source html
	request = urllib.request.urlopen(args.url[0])
	html = request.read().decode('unicode_escape')
	#write the html to a file for debug and analyzing purposes
	#file = open("playlist.html","w")
	#file.write(html)


	#find the playlist title
	pattern = re.compile("<title>(.*)</title>") 		#compile the regex to be used
	match = pattern.search(html) 						#apply that regex to the html string
	if(match):											#if a match was found, continue
		playlistTitle = match.group(0)[7:-19]			#extract and format the return string to exclude html tags etc.
	else: 												#if no match was found, exit
		print("invalid url")
		exit(1)


	#EXTRACT RELEVANT INFO
	if("playlist" in args.url[0]):
		#this regex pattern matches an area of js code at the bottom of the html containing all the relevant info for each song
		for match in re.findall(r"""id":"[\s,\S]{22}","name":"[\s,\S]*?","type":"artist",[\s,\S]*?,"name":"[\s,\S]*?","popularity""", html):
			#from that match for each song one can extract data by searching for a pattern like
			#js structure - wildcard - js structure, where the structures or keywords are unique to the data we look for
			#then, easily truncate the string on both ends to exclude the structures as we know how many characters they have

			#GET THE ARTIST
			artist = re.findall(r"""[\s,\S]*?","type":"artist","uri":"spotify""",match[37:])[0][:-32]
			playlistArtists.append(artist)
	
			#GET THE SONG TITLE
			#there are three possibilities for what can uniquely come before the song title
			title1 = re.findall("""is_playable":true,"name":"[\s,\S]*?","popularity""",match)
			title2 = re.findall("""is_playable":false,"name":"[\s,\S]*?","popularity""",match)
			title3 = re.findall(""""\},"name":"[\s,\S]*?","popularity""",match)

			#remove the regex search strings to both sides of the string
			title = (title1+title2+title3)[0][:-13]
			title = title.replace("""is_playable":true,"name":\"""","")
			title = title.replace("""is_playable":false,"name":\"""","")
			title = title.replace(""""},"name":\"""","")
			playlistTracks.append(title)

	#the same process, but applied to albums which are more regular in the way the data is structured
	if("album" in args.url[0]):
		#GET THE ARTIST
		artist = re.findall(r"""an album by [\s,\S]*? on Spotify""",html)[0][12:-11]
		print("ARTIST: " + artist)

		#GET THE SONG TITLE
		for match in re.findall(r""""is_playable":true,"name":"[\s,\S]*?","preview_url":""", html):
			#add the artist to the list of artists once for every song
			playlistArtists.append(artist)
	
			#remove the regex search strings to both sides of the string
			title = match
			title = title.replace(""""is_playable":true,"name":\"""","")
			title = title.replace("""","preview_url":""","")
			playlistTracks.append(title)

	#output the info that was found to the console
	print()
	if("album" in args.url[0]):
		print("ALBUM TILE:")
	else:
		print("PLAYLIST TILE:")
	print(playlistTitle)
	print()
	for i in range(len(playlistTracks)):
		print(playlistTracks[i] + " " + playlistArtists[i])
	print()

except Exception as e:
	raise
else:
	pass
finally:
	pass




#DOWNLOAD THE LIST OF TRACKS FROM YOUTUBE
foldername = re.sub(r"\s+", '-', playlistTitle)

#first, encapsulate the download and conversion process into functions to enable multithreading
def download(index=0):
	filename = re.sub(r"\s+", '-', playlistTracks[index]) + "-" + re.sub(r"\s+", '-', playlistArtists[index])

	#prepare and format the command used to download the song for subprocess.run()
	cmd = command + " --output /" + foldername + "/" + filename + ".%(ext)s"
	arguments = cmd.split()
	arguments.append("""ytsearch:"""+playlistTracks[index] + " " + playlistArtists[index] + searchKeywords)

	try:
		#then, run the command (stout=null so that concurrent threads dont spam the console with feedback)
		subprocess.run(arguments,stdout=subprocess.DEVNULL)
		print("("+str(index+1)+"/"+str(len(playlistTracks))+") downloaded : "+playlistTracks[index] + " by " + playlistArtists[index])
	except Exception as e:
		raise


def convert():
	#CONVERT M4A TO MP3 (if flag is set)
	for file in os.listdir("./"+foldername+"/"):
		if(file.endswith(".m4a")):
			try:
				subprocess.run(["ffmpeg","-y","-i","./"+foldername+"/"+file,"./"+foldername+"/"+file[:-4]+".mp3"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				if(os.path.exists("./"+foldername+"/"+file[:-4]+".mp3")):
					os.remove("./"+foldername+"/"+file)
					print(file + " converted")
			except Exception as e:
				raise


#delete any leftover temp files				
def cleanup():
	for file in os.listdir("./"+foldername+"/"):
		if(file.endswith(".temp")):
			#delete any leftover temp files
			try:
				os.remove("./"+foldername+"/"+file)
			except Exception as e:
				raise

#run downloads in parallel via multithreading 
print()
print("DOWNLOADING...")
#use a ThreadPoolExecutor to handle multithreading when downloading while limiting the number of threads to --threads
with ThreadPoolExecutor(max_workers=maxThreads) as executor:
	for i in range(len(playlistTracks)):
		executor.submit(download, (i))


#if --mp3 is enabled, convert all downloaded videos using multithreading
if(args.fast and args.mp3):
	print()
	print("CONVERTING ...")
	with ThreadPoolExecutor(max_workers=maxThreads) as executor:
		for i in range(len(playlistTracks)):
			executor.submit(convert)
	convert()

cleanup()
