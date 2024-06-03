# how to do things

# README Changelog
6/3/2024
- add bits about correcting results songs that were tagged wrong

4/27/2024
- added tagging new submissions instructions

4/1/2024
- created file


# Tagging new submissions
1. archive all old submissions from the previous month from the aws s3 bucket. No script for this yet, just move them into the `/upload-form-archive/mon-yyyy/` folder
2. run the song submission helper under the `~/programming/dodSubmissionsHelper` directory by using `make run` and browse to it at `localhost:4000`
3. adjust any song submissions that need to be changed, like if someone resubmitted an entry, delete the old one, fix any game names that are wrong, artist names, etc.
4. kill the dodSubmissionsHelper process
5. navigate to the `/tagSubmissionFormSongs` directory, update tag.py with the new month's album name, and insert the new album art file in the `files` directory.
6. in the same `/tagSubmissionFormSongs` directory, run `make fromScratch`. This removes all old downloaded files, redownloads, and tags them all.
7. when completed, copy all the anonymous songs from `files/newSongsAnon` and put them in the appropriate month folder in the `generator` project.


# Tallying votes and tagging results
1. take the `songs.csv` file from the `/tagSubmissionFormSongs` directory (create it with `make list`) and copy to the `/votingSource` directory
2. Run the `votes_archive.py` script from the `voting` directory to archive previous month's votes.
3. create the `votes.txt` file in the `/voting` directory by using `make fromScratch` and copy to the `/votingSource` directory
4. run the tally server by using `make start` in the `/votingSource` directory, and visit it at `localhost:8000/static/index.html`
5. make any changes to the songs by clicking the checkboxes. the leftmost checkbox when unchecked will ignore this vote 
for results. The rightmost checkbox when checked will consider the votes to be weighted in the case of song reviews.
6. click `Save Results`. This writes to the `results.json` file in the `/votingSource` directory
7. copy and save the text content from the left page to a notepad file so we can post it later
8. correct any "ARTIST" fields in the `results.json` that didnt auto fill.
9. copy the `results.json` file created in the last step back to `/tagSubmissionFormSongs`
10. update any incorrect tags for songs by running the server mentioned in `Tagging New Submissions` above.
11. run `make tagResultsWithLyrics` in `/tagSubmissionFormSongs`
12. copy all the songs from `newSongs` over to the generator's correct dodarchive directory
13. spot check all the tagged MP3 files and make corrections if needed





# TODO
- need a way to update an entry with a new mp3 easily. needs to put it up to s3 so its stored for future pulls
- add button to auto archive the previous month's tracks. names the folders automatically (or at least provides a default automatically)
- create a script to auto archive old votes from s3
- clean, combine, and organize the `voting` and `votingSource` folders
- move the dodSubmissionsHelper project into this repo
- make a script that can auto generate the variants of the banner art that I need
- make the `tag.py` script read the month name info from a cfg file so we dont have to edit the source every month
- make the voting tally script auto-flag anybody who has too many "average +0.00" votes because those are usually incomplete


# notes on downloader from first/second real use case (this section is very old)
- people resubmitting votes is weird to deal with. maybe a list function like the song downloader can help put things into csv and locate and delete old votes. OR the voting script just looks and identifies multiple votes from same address, only uses latest.
- some kinda uber script that can take all the data from the songs 'list.csv' and the output from votes.exe and fill in all the artist names for me, AND update all the mp3 track listings/rankings
- throw a normal error when the album art is missing
- songs that need to be moved to an alt during/after voting are hard to deal with
- sometimes votes come in inconsistently such as when we moved minorffanatic's entry to alts but people still had the original votes sheet open
- add a cache
