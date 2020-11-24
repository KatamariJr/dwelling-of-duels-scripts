#!/usr/bin/python

import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.tools import argparser

import api_stuff


def initialize_upload(youtube, options):
    """init upload to youtube"""
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    formatted_description = options.description.replace('\\n', '\n')

    body = dict(
        snippet=dict(
            title=options.title,
            description=formatted_description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )
    api_stuff.resumable_upload(insert_request)


if __name__ == '__main__':
    argparser.add_argument("--file", required=True, help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description",
                           default="Test Description")
    argparser.add_argument("--category", default="22",
                           help="Numeric video category. " +
                           "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
                           default="")
    argparser.add_argument("--privacyStatus", choices=api_stuff.VALID_PRIVACY_STATUSES,
                           default=api_stuff.VALID_PRIVACY_STATUSES[0],
                           help="Video privacy status.")
    ARGS = argparser.parse_args()

    if not os.path.exists(ARGS.file):
        exit("Please specify a valid file using the --file= parameter.")

    YOUTUBE = api_stuff.upload_get_authenticated_service(ARGS)
    try:
        initialize_upload(YOUTUBE, ARGS)
    except HttpError:
        import sys
        e = sys.exc_info()[1]
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
