# how to do DoD things

# README Changelog
11/25/2024
- rewritten to simplify paths

6/3/2024
- add bits about correcting results songs that were tagged wrong

4/27/2024
- added tagging new submissions instructions

4/1/2024
- created file

# Submission/Voting System Components and Locations

Submissions Helper - `~/dwelling-of-duels/scripts/submissionsHelper`
Submissions Archiver - TODO
Tag Submission Form Songs - `~/dwelling-of-duels/scripts/tagSubmissionFormSongs`
Votes Helper - `~/dwelling-of-duels/scripts/voting`
Generator - `~/dwelling-of-duels/generator`

# Note
All instructions in this file assuming you are using the Terminal.

# Tagging new submissions
1. Archive all old submissions from the previous month from the aws s3 bucket. No script for this yet, just move them
   into the `/upload-form-archive/mon-yyyy/` folder
    1. TODO - modify the votes archive script to also work on this step
2. Navigate to the **SubmissionsHelper** directory and start the tool by using `make run` and browse to it at `localhost:4000`
3. Address any song submissions that need to be changed.
    1. Check for the same song being resubmitted. In this case, delete the older entry after ensuring the tags are the same.
    2. Check for Artist+Game Names that are incorrect. They should match what is used on the rest of the site, with
       exactly the same punctuation and capitalization.
4. Terminate the dodSubmissionsHelper by focusing on the window and pressing Control+C
5. Navigate to the **Tag Submission Form Songs** directory, update tagInfo.cfg with the new month's album name, and insert
   the new album art file in the `files` directory.
6. In the same directory, run `make fromScratch`. This removes all old downloaded files, redownloads, and tags them all.
    1. Note: Any messages like "Non standard genre name" that you see can be safely ignored.
7. When completed, copy all the anonymous songs from `/tagSubmissionFormSongs/files/newSongsAnon` and put them in the
   appropriate month folder in the **Generator** project.


# Tallying votes and tagging results
1. update any incorrect tags for songs by running the **SubmissionsHelper** server mentioned in `Tagging New Submissions` above.
2. Navigate to the **Tag Submission Form Songs** directory and run `make songs.csv`. Copy this file to the
   **Votes Helper** directory
3. Navigate to the **Votes Helper** directory and run the `votes_archive.py` script to archive previous month's votes.
   Follow the prompts.
4. Create the `votes.txt` file by using `make fromScratch`.
5. Run the tally server by using `make helper`, and visit it from Firefox at `localhost:8000/static/index.html`
6. Make any changes to the votes by clicking the checkboxes. The leftmost checkbox will consider this vote for results. You
   can uncheck it to essentially ignore a vote submission. The rightmost checkbox can be checked to indicate the submitter
   gave reviews and their vote should be weighted.
7. Copy and save the text content from the left page to a notepad file so we can post it later
8. Click `Save Results`. This writes to the `results.json` file in **Votes Helper** directory.
9. Open up `results.json` in the text editor. Correct any "ARTIST" fields that didnt auto fill.
10. copy the `results.json` file created in the last step to the **Tag Submissions Form Songs** directory.
11. run `make tagResultsWithLyrics`.
12. copy all the songs from `newSongs` over to the generator's correct dodarchive directory
13. spot check all the tagged MP3 files and make corrections with MP3Tag if needed.





# TODO
- need a way to update an entry with a new mp3 easily. needs to put it up to s3 so its stored for future pulls
- add button to auto archive the previous month's tracks. names the folders automatically (or at least provides a default automatically)
- make the voting tally script auto-flag anybody who has too many "average +0.00" votes because those are usually incomplete
- add a button to let me view the raw json for an entry (and maybe edit)
- make a way to alert the submitter of a song if a voter had submitted high deviance votes that strongly favored the submitter (ballot stuffing), just include the email address and a generic notice. we could then track how many times this happens


# notes on downloader from first/second real use case (this section is very old)
- people resubmitting votes is weird to deal with. maybe a list function like the song downloader can help put things into csv and locate and delete old votes. OR the voting script just looks and identifies multiple votes from same address, only uses latest.
- some kinda uber script that can take all the data from the songs 'list.csv' and the output from votes.exe and fill in all the artist names for me, AND update all the mp3 track listings/rankings
- throw a normal error when the album art is missing
- songs that need to be moved to an alt during/after voting are hard to deal with
- sometimes votes come in inconsistently such as when we moved minorffanatic's entry to alts but people still had the original votes sheet open
