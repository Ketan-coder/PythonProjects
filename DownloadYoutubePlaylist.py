# Importing the module
from pytube import Playlist
# import os

# Taking the playlist link from the user
playlist_url = input("Enter the playlist URL: ")

# Creating a Playlist object
playlist = Playlist(playlist_url)

# Looping through all the videos in the playlist
i = 0
for video in playlist.videos:
    # Downloading each video to given directory with both given commands
    # video.streams.first().download(output_path="D://Videos//Course//Statical techniques",filename_prefix="{i}-")
    # video.streams.first().download(output_path="D://Music//YoutubeMusic",filename=f"{i} + {video.title}")
    # To Download only audio
    video.streams.filter(only_audio=True).get_audio_only().download(output_path="D://Music//YoutubeMusic",filename_prefix=f"{i}-")
    i += 1
    print(f"Downloaded {video.title}")

print("Finished")
