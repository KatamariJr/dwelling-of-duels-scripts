#!/usr/bin/env bash

# sync changed json files back up to s3
aws s3 sync --exclude=* --include=*.json --exclude="newSongs/*" ./files s3://dwellingofduels-static-site/upload-form 
