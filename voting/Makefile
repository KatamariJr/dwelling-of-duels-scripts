.PHONY: fromScratch clean download votes start

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

start:
	python3 -m uvicorn votingNew:app --reload