.PHONY: fromScratch clean download votes

fromScratch:
	$(MAKE) clean
	$(MAKE) download
	$(MAKE) votes

clean:
	rm -r ./files
	rm ./votes.txt

download:
	./download.sh

votes:
	python ./votes_compile.py
