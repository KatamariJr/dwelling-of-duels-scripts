

# TODO
- ability to move a submission to "deleted" which wont let them be tagged but we can still see they were deleted. 
  - deleting something from the ui should remove and add the row to the deleted table
  - maybe add a "deleteReason" field that we can save in the json?
- highlight submitters who may have been on too many tracks for the month.
- automatically suggest corrections for common misspellings.
- add button and date picker to auto archive any songs from before the last deadline date
- add a cache for s3 file data, insert files into the cache if they get saved over so that we serve latest stuff. cache files for 5 minutes. 
- handle orphaned files and delete them