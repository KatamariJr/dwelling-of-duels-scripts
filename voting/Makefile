.PHONY: fromScratch clean download votes helper

fromScratch:
	$(MAKE) clean
	$(MAKE) download
	$(MAKE) votes

clean:
	rm -rf ./files
	rm -f ./votes.txt

download:
	./download.sh

votes:
	python3 ./votes_compile.py

archive:
	python3 ./votes_archive.py

helper:
	python3 -m uvicorn voting_helper:app --reload