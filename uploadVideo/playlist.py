#!/usr/bin/python

import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

import api_stuff

def create_playlist(youtube,args):
    # This code creates a new, private playlist in the authorized user's channel.

    playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=args.title,
                description="Dwelling of Duels"
            ),
            status=dict(
                privacyStatus="private"
            )
        )
    ).execute()

    print("New playlist id: %s" % playlists_insert_response["id"])
    return playlists_insert_response["id"]


def addVidsToPlaylist(youtube, playlistID, allIDs):
    print(allIDs)
    for id in allIDs:
        try:
            playlist_items_insert(youtube,
                                  {'snippet.playlistId':playlistID,
                                   'snippet.resourceId.kind': 'youtube#video',
                                   'snippet.resourceId.videoId': id,
                                   'snippet.position': ''},
                                  part='snippet')
        except HttpError:
            import sys
            e = sys.exc_info()[1]
            if e.resp.status == 404:
                continue
            else:
                exit()
    return


def playlist_items_insert(client, properties, **kwargs):
    resource = api_stuff.build_resource(properties)
    response = client.playlistItems().insert(
        body=resource,
        **kwargs
    ).execute()

    if 'id' in response:
        print("Successfully added")
        return response

    exit("returned unexpected response")


def prepend(originalfile, string):
    with open(originalfile, 'r') as f:
        with open('newfile.txt', 'w') as f2:
            f2.write(string)
            f2.write(f.read())
    os.remove(originalfile)
    os.rename('newfile.txt', originalfile)


if __name__ == '__main__':
    argparser.add_argument("--file", required=False, help="list of IDs to link in playlist")
    argparser.add_argument("--title", help="Playlist title", default="Test Title")
    argparser.add_argument("--description", help="Playlist description",
                           default="Test Description")
    argparser.add_argument("--privacyStatus", choices=api_stuff.VALID_PRIVACY_STATUSES,
                           default=api_stuff.VALID_PRIVACY_STATUSES[0],
                           help="Video privacy status.")
    args = argparser.parse_args()
    youtube = api_stuff.read_write_get_authenticated_service()
    try:
        id = create_playlist(youtube, args)
        arrID = api_stuff.readFromFile(args.file)

        addVidsToPlaylist(youtube, id, arrID)
        prepend(args.file, id+"\n")

    except HttpError:
        import sys
        e = sys.exc_info()[1]
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
