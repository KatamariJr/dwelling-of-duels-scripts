.PHONY: fromScratch clean download votes helperServer

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
	python ./votes_compile.py

helperServer:
	python3 -m uvicorn voting_helper:app --reload