# Dwelling of Duels Youtube Utility Script

The primary script helps with multiple steps in the monthly DoD flow of uploading to YouTube:
- Modify ambiguous dashes in filenames.
- Converting audio files (mp3) into video files (mp4) featuring a static image.
- Create a playlist for the monthly song set.
- Upload videos (private) to the YouTube channel (authorization required) and add them to the playlist

A secondary script does this:
- Apply public visibility to all videos and playlists after confirmation of accuracy.


# How to use
1. install ffmpeg
1. install python 
1. install python dependencies by running `pip install -r requirements.txt`
1. copy the song files and album art image into the `copySongsHere` folder
1. create an `uploadSettings.txt` file like the `uploadSettings_example.txt` file.
1. run the primary script `createAndUploadFromMP3.bat`. This should prompt you to login to google. This creates all the video files and begins uploading them.
1. After verifying all the videos look good on the youtube channel, run the secondary script `setToPublic.bat` to make the playlist and videos all public.


# TODO
- make the ambiguous dash step happen before any video creation, and cache those results in a txt file in case of a restart
- make a handy cli tool that can start or resume execution from any of the steps in case of errors
- make the whole script able to terminate itself if an error occurs in the ffmpeg process or upload process
- playlist addiion and public setting are wonky