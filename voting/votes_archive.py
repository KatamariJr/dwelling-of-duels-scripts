import os
import boto3
import json
import datetime
import time

BUCKET_NAME = 'dwellingofduels-static-site'
VOTES_FOLDER = 'voting-form'
ARCHIVE_FOLDER = 'voting-form-archive'

# Configure Boto3 client
s3 = boto3.client('s3')


def get_file_metadata(bucket_name: str, key: str) -> str:
    """Retrieves and extracts 'submissionTime' from JSON file in S3."""
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    data = json.loads(obj['Body'].read().decode('utf-8'))
    return data['submissionTime'][:26]


def bisect_submission_times(metadata: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """Bisects submission times around the average submission time."""

    string_format = '%Y-%m-%dT%H:%M:%S.%f'

    submission_datetimes = [
        time.mktime(datetime.datetime.strptime(submission_time, string_format).timetuple())
        for submission_time in metadata.values()
    ]

    average_datetime = sum(submission_datetimes) / len(submission_datetimes)

    print("Bisect date is:", datetime.datetime.fromtimestamp(average_datetime))

    earlier_submissions = {
        filename: submission_time
        for filename, submission_time in metadata.items()
        if time.mktime(datetime.datetime.strptime(submission_time, string_format).timetuple()) < average_datetime
    }
    later_submissions = {
        filename: submission_time
        for filename, submission_time in metadata.items()
        if time.mktime(datetime.datetime.strptime(submission_time, string_format).timetuple()) >= average_datetime
    }

    return earlier_submissions, later_submissions


# Main logic
file_metadata: dict[str, str] = {}
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=VOTES_FOLDER)

print("Processing vote files")
for page in pages:
    if 'Contents' in page:
        for obj in page['Contents']:
            key = obj['Key']
            if ARCHIVE_FOLDER in key:
                continue

            file_metadata[key] = get_file_metadata(BUCKET_NAME, key)

print('Found {} vote files'.format(len(file_metadata)))
print('Bisecting dates')

earlier_submissions, later_submissions = bisect_submission_times(file_metadata)

# find min and max dates
min_date: str | None = None
max_date: str | None = None
for filename in earlier_submissions:
    if min_date is None:
        min_date = earlier_submissions[filename]
        max_date = earlier_submissions[filename]
        continue
    if earlier_submissions[filename] < min_date:
        min_date = earlier_submissions[filename]
    if earlier_submissions[filename] > max_date:
        max_date = earlier_submissions[filename]

print('Preparing to archive {} vote files, with dates ranging from {} to {}'.format(len(earlier_submissions), min_date, max_date))

confirm = input("Proceed with moving earlier votes? (y/n): ")
if confirm.lower() != 'y':
    print("Operation canceled.")
    exit()

dest_folder = input("Enter destination folder name (ex: sep-2023): ")

for filename, submission_time in earlier_submissions.items():
    source_key = filename
    dest_key = f"{ARCHIVE_FOLDER}/{dest_folder}/{os.path.basename(filename)}"

    copy_source = {
        'Bucket': BUCKET_NAME,
        'Key': source_key
    }

    try:
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=copy_source, Key=dest_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=source_key)
        print(f"Moved {filename} to {dest_key}")
    except Exception as e:
        print(f"Error moving {filename}: {e}")

print("Operation completed.")