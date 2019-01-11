REM put this file and ffmpeg.exe into a folder that contains mp3 files and your artwork. run batch file.

REM if you want to use something other than a jpg just change this line
for %%i in (*.jpg) do SET img=%%i

REM if you want to use some other kind of music format besides mp3 just change this line
for %%i in (*.mp3) do ffmpeg -r 1 -loop 1 -i %img% -i "%%i" -acodec copy -r 1 -shortest -vf scale=1280:720 "%%~ni.mp4"
