xcopy .\copySongsHere\*.mp3 .\makeVideo /Y

xcopy .\copySongsHere\*.jpg .\makeVideo /Y

type .\copySongsHere\uploadSettings.txt

echo "Is the above information correct??????"

pause

xcopy .\copySongsHere\uploadSettings.txt .\uploadVideo /Y

cd makeVideo

call videoCreator.bat

DEL *.mp3

DEL *.jpg

MOVE *.mp4 ..\uploadVideo\

cd ..\uploadVideo

xcopy uploadedIDs.txt uploadedIDs_old.txt /Y

del uploadedIDs.txt

call upload.bat

pause

DEL *.mp4

call playlist.bat

pause

REM write seperate batch file to use uploadedIDs.txt to set all privacy options to public when acceptable
