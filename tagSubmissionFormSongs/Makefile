.PHONY: tag fromScratch tag-with-lyrics download lyrics cleanTaggedSongs cleanDownloadedData download songs.csv

tagResultsWithLyrics:
	$(MAKE) tagResults
	$(MAKE) lyrics

tagResults:
	$(MAKE) cleanTaggedSongs
	python tag.py results.json

tagWithLyrics:
	$(MAKE) tag
	$(MAKE) lyrics

tag:
	$(MAKE) cleanTaggedSongs
	python tag.py

list:
	python list.py

lyrics:
	python lyrics.py

cleanTaggedSongs:
	rm -f files/newSongs/*
	rm -f files/newSongsAnon/*

cleanAll:
	$(MAKE) cleanSongs
	$(MAKE) cleanMetadata

cleanMetadata:
	rm -f ./files/*.json

cleanSongs:
	rm -f ./files/*.mp3

download:
	set -o errexit
	aws s3 sync s3://dwellingofduels-static-site/upload-form ./files --exclude="*deleted*"

fromScratch:
	$(MAKE) cleanTaggedSongs
	$(MAKE) cleanAll
	$(MAKE) download
	$(MAKE) list
	$(MAKE) tagWithLyrics

update: # sync changed json files back up to s3
	aws s3 sync --exclude=* --include=*.json --include=*.mp3 --exclude="newSongs/*" --exclude="newSongsAnon/*" --exclude="deleted" ./files s3://dwellingofduels-static-site/upload-form
