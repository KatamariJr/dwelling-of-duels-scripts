@echo off
echo Twitch chatlog getter
set /p id="Enter Twitch VOD ID: "

call TwitchDownloaderCLI.exe -m ChatDownload -o temp.txt -u %id%

type "temp.txt" | find /v "" > "log%id%.log"

DEL "temp.txt"

echo Log dumped to log%id%.log
pause