put "video creator.bat" and "ffmpeg.exe" into a folder that contains mp3 files and your artwork as a jpg. run "video creator.bat"



VVV stolen from superuser.stackoverflow VVV

FFmpeg will try to pick the best codec automatically, depending on the extension of your output file.

Update: I noticed YouTube has difficulty processing the video (gets stuck at 95%) I think because there's only one frame. The solution I found to make YouTube happy: add more frames. Also, I added-acodec copy to preserve the audio quality. You need -shortest or it loops forever. (It stops at the end of the shortest stream, which is the audio, because the image loop is infinite.) The order of your options is very important for speed, as filters (and such) are processed in the order you specify. If you change the order of these parameters, the results are dramatically different.

Also notice that I set the frame rate twice, that's not an accident--the first frame rate is for the input, second is for the output. If you do this correctly, there should only be one frame per second of video, which means it encodes relatively fast. Also I set the resolution to 720p here, which means you should get HD audio on YouTube :-)



ffmpeg -r 1 -loop 1 -i image.jpg -i audio.wav -acodec copy -r 1 -shortest -vf scale=1280:720 ep1.flv
