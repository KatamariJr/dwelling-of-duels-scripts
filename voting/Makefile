.PHONY: fromScratch clean download votes

fromScratch:
	$(MAKE) clean
	$(MAKE) download
	$(MAKE) votes

clean:
	rm -r ./files

download:
	./download.sh

votes:
	python ./votes_compile.py