# how to do things as of 4/1/2024

# Changelog
4/1/2024
- created file


# Tagging new submissions





# Tallying votes and tagging results
1. take the `songs.csv` file from the `/tagSubmissionFormSongs` directory (create it with `make list`) and copy to the `/votingSource` directory
2. create the `votes.txt` file in the `/voting` by using `make votes` and copy to the `/votingSource` directory
3. run the tally server by using `make start` in the `/votingSource` directory
4. make any changes to the songs by clicking the checkboxes. the leftmost checkbox when unchecked will ignore this vote 
for results. The rightmost checkbox when checked will consider the votes to be weighted in the case of song reviews.
5. click `Save Results`. This writes to the `results.json` file in the `/votingSource` directory
6. copy and save the text content from the left page to a notepad file so we can post it later
7. copy the `results.json` file created in the last step back to `/tagSubmissionFormSongs`
8. update any incorrect tags for songs by running the server mentioned in `Tagging New Submissions` above.
9. run `make tagResultsWithLyrics` in `/tagSubmissionFormSongs`
10. copy all the songs from `newSongs` over to the generator's correct dodarchive directory





# TODO
- need a way to update an entry with a new mp3 easily. needs to put it up to s3 so its stored for future pulls
- add button to auto archive the previous month's tracks. names teh folders automatically (or at least provides a default automatically)



# notes on downloader from first/second real use case (this section is very old)

- people resubmitting votes is weird to deal with. maybe a list function like the song downloader can help put things into csv and locate and delete old votes. OR the voting script just looks and identifies multiple votes from same address, only uses latest.

- some kinda uber script that can take all the data from the songs 'list.csv' and the output from votes.exe and fill in all the artist names for me, AND update all the mp3 track listings/rankings

- throw a normal error when the album art is missing

- songs that need to be moved to an alt during/after voting are hard to deal with

- sometimes votes come in inconsistently such as when we moved minorffanatic's entry to alts but people still had the original votes sheet open

- add a cache
