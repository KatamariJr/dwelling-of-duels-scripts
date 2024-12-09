#!/usr/bin/env python3

import os
import boto3
import json
import datetime
import time

BUCKET_NAME = 'dwellingofduels-static-site-dev'
SUBMISSIONS_FOLDER = 'upload-form'
ARCHIVE_FOLDER = 'upload-form-archive'

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
print("Operating on bucket:", BUCKET_NAME)
file_metadata: dict[str, str] = {}
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=SUBMISSIONS_FOLDER)

print("Processing submission metadata files")
for page in pages:
    if 'Contents' in page:
        for obj in page['Contents']:
            key = obj['Key']
            if ARCHIVE_FOLDER in key:
                # print("skipping the archive folder")
                continue
            if "deleted" in key:
                # print("skipping the deleted folder")
                continue
            if key.endswith('.json'):
                file_metadata[key] = get_file_metadata(BUCKET_NAME, key)


print('Found {} submission files'.format(len(file_metadata)))
print('Bisecting dates...')

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

print('Preparing to archive {} sets of submissions (json and mp3), with dates ranging from {} to {}'.format(len(earlier_submissions), min_date, max_date))

confirm = input("Proceed with moving earlier submissions? (y/n): ")
if confirm.lower() != 'y':
    print("Operation canceled.")
    exit()

dest_folder = input("Enter destination folder name (ex: sep-2023): ")

for filename, submission_time in earlier_submissions.items():
    filename_without_extension = os.path.splitext(filename)[0]
    basename = os.path.basename(filename)
    key_without_extension = os.path.splitext(basename)[0]

    json_source_key = filename
    json_dest_key = f"{ARCHIVE_FOLDER}/{dest_folder}/{key_without_extension}.json"

    mp3_source_key = f"{filename_without_extension}.mp3"
    mp3_dest_key = f"{ARCHIVE_FOLDER}/{dest_folder}/{key_without_extension}.mp3"

    json_copy_source = {
        'Bucket': BUCKET_NAME,
        'Key': json_source_key
    }

    mp3_copy_source = {
        'Bucket': BUCKET_NAME,
        'Key': mp3_source_key
    }

    try:
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=json_copy_source, Key=json_dest_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=json_source_key)
        print(f"Moved {json_source_key} to {json_dest_key}")
    except Exception as e:
        print(f"Error moving {json_source_key} to {json_dest_key}: {e}")
        exit(1)

    try:
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=mp3_copy_source, Key=mp3_dest_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=mp3_source_key)
        print(f"Moved {mp3_source_key} to {mp3_dest_key}")

    except Exception as e:
        print(f"Error moving {mp3_source_key} to {mp3_dest_key}: {e}")
        exit(1)

# move entire 'deleted' folder contents
deleted_source_folder_prefix = f"{SUBMISSIONS_FOLDER}/deleted"
deleted_dest_folder_prefix = f"{ARCHIVE_FOLDER}/{dest_folder}/deleted/"
print("Processing deleted submissions folder")
try:
    file_metadata: dict[str, str] = {}
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=deleted_source_folder_prefix)
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                base_filename = os.path.basename(key)
                s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': key}, Key=deleted_dest_folder_prefix + base_filename)
                s3.delete_object(Bucket=BUCKET_NAME, Key=key)

    print(f"Moved folder {deleted_source_folder_prefix} to {deleted_dest_folder_prefix}")
except Exception as e:
    print(f"Error moving folder {deleted_source_folder_prefix} to {deleted_dest_folder_prefix}: {e}")
    exit(1)

print("Operation completed.")