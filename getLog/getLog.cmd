@echo off
echo Twitch chatlog getter
set /p id="Enter Twitch VOD ID: "

call twitch-chatlog -l 0 %id% > "temp"

type "temp" | find /v "" > "log%id%.log"

DEL "temp"

echo Log dumped to log%id%.log
pause