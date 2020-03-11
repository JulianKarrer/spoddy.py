# spoddy.py

A python based command line utility to automatically find all track titles and artists in a Spotify playlist, search for each track on Youtube and download it as an mp3.  

Just pass the open.spotify.com/... - link as an argument to get started.

## Features

- Download entire Spotify Playlists or Albums via Youtube
- Completely legal, no ripping involved. As a trade-off, some songs might not be found or you might download wrong versions
- Uses multithreading to enable faster concurrent downloads

## Prerequisites

This script requires:
- Python version >= 3.5  
- youtube-dl to download the tracks. 

   - For UNIX (Linux, OS X, etc.), use: 
  
   ```
   sudo pip install --upgrade youtube_dl
   ```

   - Windows users can download the latest .exe [here.](https://yt-dl.org/latest/youtube-dl.exe)  

- optionally: ffmpeg to enable faster downloads. Get ffmpeg [here.](https://www.ffmpeg.org/download.html)

Make sure youtube-dl and ffmpeg are recognized commands on your system by adding them to the PATH or copying each .exe to spoddy.py's working directory.

## Usage

To view options and flags, type:

```
py spoddy.py -h
```
Example usage could look like this:
```
py spoddy.py https://open.spotify.com/album/6FjWnzaTZawabmBcUaSNGk --fast --mp3
```