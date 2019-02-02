xcopy .\copySongsHere\*.mp3 .\makeVideo /Y

xcopy .\copySongsHere\*.jpg .\makeVideo /Y

type .\copySongsHere\uploadSettings.txt

echo "Is the above information correct??????"

pause

xcopy .\copySongsHere\uploadSettings.txt .\uploadVideo /Y

cd makeVideo

call videoCreator.bat

MOVE *.mp4 ..\uploadVideo\

cd ..\uploadVideo

xcopy uploadedIDs.txt uploadedIDs_old.txt /Y

DEL uploadedIDs.txt

call upload.bat

pause

call playlist.bat

pause

cd ..

call clean.bat
