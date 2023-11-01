#!/usr/bin/env bash

# sync changed json files back up to s3
aws s3 sync --exclude=* --include=*.json --include=*.mp3 --exclude="newSongs/*" --exclude="newSongsAnon/*" ./files s3://dwellingofduels-static-site/upload-form 
