#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
      message=MISSING_CLIENT_SECRETS_MESSAGE,
      scope=YOUTUBE_READ_WRITE_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))

def playlist_items_insert(client, properties, **kwargs):
  resource = build_resource(properties)

  response = client.playlistItems().insert(
    body=resource,
    **kwargs
  ).execute()

  if 'id' in response:
      print("Successfully added")
      return (response)
  else:
      exit("returned unexpected response")


def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]

      # For properties that have array values, convert a name like
      # "snippet.tags[]" to snippet.tags, and set a flag to handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

def readFromFile(filename):
  f =open(filename, "r")
  arr = []
  for line in f:
      if len(line) == 0:
          continue
      line = line.replace("\n", "")
      line = line.replace("\r", "")
      arr.append(line)
  f.close()
  return arr

def videos_update(youtube, properties, **kwargs):
    resource = build_resource(properties)

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
    resource = build_resource(properties)

    response = youtube.playlists().update(
        body=resource,
        **kwargs
    ).execute()

    if 'id' in response:
        print("Successfully set playlist to public")

    return response

def playlist_list(youtube, properties, **kwargs):

    resource = build_resource(properties)

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

  youtube = get_authenticated_service()
  try:

      arrID = readFromFile(args.file)

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
