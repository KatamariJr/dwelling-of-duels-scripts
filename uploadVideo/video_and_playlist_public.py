#!/usr/bin/python


from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

import api_stuff

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




def videos_update(youtube, properties, **kwargs):
    resource = api_stuff.build_resource(properties)
    response = youtube.videos().update(
        body=resource,
        **kwargs
    ).execute()

    if 'id' in response:
        print("Successfully set video to public")

    return response


def setVideosPublic(youtube, allIDs):
    for id in allIDs:
        try:
            print("video id: {}".format(id))
            videos_update(youtube,
                          {'id':id,
                           'status.privacyStatus': 'public'},
                          part='status')
        except HttpError:
            import sys
            e = sys.exc_info()[1]
            if (e.resp.status == 404 or e.resp.status == 403):
                continue
            else:
                print(e.resp)
                exit()
    return

def playlist_update(youtube, properties, **kwargs):
    resource = api_stuff.build_resource(properties)
    response = youtube.playlists().update(
        body=resource,
        **kwargs
    ).execute()
    if 'id' in response:
        print("Successfully set playlist to public")

    return response

def playlist_list(youtube, properties, **kwargs):
    resource = api_stuff.build_resource(properties)
    response = youtube.playlists().list(
        **kwargs
    ).execute()

    return response


def setPlaylistPublic(youtube, playlistID):
    playlist = playlist_list(youtube, {'id':playlistID}, part='id,snippet', id=playlistID)
    playlistTitle = playlist['items'][0]['snippet']['title']
    playlistDesc = playlist['items'][0]['snippet']['description']

    print("Playlist id {}".format(playlistID))
    try:
        playlist_update(youtube,
                        {'id':playlistID,
                         'status.privacyStatus': 'public',
                         'snippet.title': playlistTitle,
                         'snippet.description': playlistDesc},
                        part='status,snippet')
    except HttpError:
        import sys
        e = sys.exc_info()[1]
        if e.resp.status == 404:
            print("a")
        else:
            print(e.resp)
            exit()
    return


if __name__ == '__main__':
    argparser.add_argument("--file", required=False, help="list of IDs to set to public")
    args = argparser.parse_args()
    youtube = api_stuff.read_write_get_authenticated_service()
    try:
        arrID = api_stuff.readFromFile(args.file)
        playlistID = arrID[0]
        arrID = arrID[1:]
        setVideosPublic(youtube, arrID)
        print("videos done")
        setPlaylistPublic(youtube, playlistID)
        print("playlist done")

    except HttpError:
        import sys
        e = sys.exc_info()[1]
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
