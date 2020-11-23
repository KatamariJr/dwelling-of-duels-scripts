#!/usr/bin/env python3

import os
import re
import csv
import sys
import datetime
import jinja2
import hashlib
import calendar
import datetime
import functools
import configparser

from slugify import slugify
from hsaudiotag import id3v2, auto as parse_id3


open = functools.partial(open, encoding='utf-8')

id3v2.re_numeric_genre = re.compile('always-fail')

HREF_RE = re.compile(r'(deploy/(?:.+/)?)"')

OUT_DIR = 'deploy' + os.sep
TEMPLATE_DIR = 'templates' + os.sep

TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

TEMPLATES.filters['slugify'] = slugify

CONFIG = configparser.ConfigParser()
CONFIG.read('site.cfg')

VOTING = CONFIG['dod_site'].getboolean('voting')
ARCHIVE_DIR = CONFIG['dod_site'].get('archive_dir')
DEADLINE_TIME = CONFIG['dod_site'].get('deadline_time')

DATA = []

DUEL_REPLACEMENTS = [
    ('DoD04-CW', 'DoD04-10'),
    ('DoD05-JO', 'DoD05-07'),
    ('DoD05-TS', 'DoD05-02'),
    ('DoD06-JO', 'DoD06-01'),
    ('DoD06-TS', 'DoD06-02'),
    ('DoD09-JO', 'DoD09-01'),
    ('DoD10-JO', 'DoD10-01'),
    ('DoD11-11S', 'DoD11-11'),
    ('DoD13-0910', 'DoD13-09')
]

ARTIST_WHITELIST = [
    'Evil(I)(I)'
]

CSS_FILES = [
    'bootstrap.css',
    'sortable.css',
    'slider.css',
    'style.css',
	'nanoscroller.css'
]

JS_FILES = [s.replace('/', os.sep) for s in [
    'lib/jquery.js',
	'lib/jquery.nanoscroller.min.js',
	'lib/jquery.floatThead.min.js',
    'lib/bootstrap-transition.js',
    'lib/bootstrap-collapse.js',
    'lib/sortable.js',
    'lib/slider.js',
	'lib/howler.min.js',
    'make-filter.js',
    'player.js',
    'voting.js',
	'randomPlayer.js'
]]


def build_data():
    for d in os.listdir(ARCHIVE_DIR):
        path = os.path.join(ARCHIVE_DIR, d)

        if not os.path.isdir(path):
            continue

        DATA.extend(get_month_data(path))

    set_template_globals()


def fix_duel_name(duel):
    for x, y in DUEL_REPLACEMENTS:
        duel = duel.replace(x, y)

    return duel


def fix_artist(artist):
    if artist not in ARTIST_WHITELIST:
        artist = artist.replace(' (', ', ').replace(')', '')

    return artist


def get_month_data(month_dir):
    songs = []

    month_files = os.listdir(month_dir)

    song_filenames = [f for f in month_files if f.endswith('.mp3')]

    max_rank = max([f.split("-")[0] for f in song_filenames if not f.startswith('ZZ')], default=0)

    youtube_link = get_youtube_link(month_dir)

    for f in song_filenames:
        song_path = os.path.join(month_dir, f)

        song_data = parse_id3.File(song_path)

        duel = fix_duel_name(song_data.album).replace('DoD', '', 1)

        month_number = duel.split('-')[1].split(':')[0]

        artist = fix_artist(song_data.artist)

        month_dir_part = month_dir.replace(ARCHIVE_DIR, '').strip(os.sep)

        songs.append({
            'rank': f.split('-')[0].replace('tie', ''),
            'max_rank': max_rank,
            'artists': artist.split(', '),
            'multiple_artists': len(artist.split(', ')) > 1,
            'games': song_data.genre.split(', '),
            'multiple_games': len(song_data.genre.split(', ')) > 1,
            'title': song_data.title,
            'duration': song_data.duration,
            'duel': duel,
            'link': f,
            'theme': duel.split(': ', 1)[1],
            'year': '20' + duel.split('-')[0],
            'month': month_number,
            'month_name': calendar.month_name[int(month_number)],
            'month_dir': month_dir_part,
            'has_log': month_dir_part + '.log' in month_files,
            'has_banner': month_dir_part + '.jpg' in month_files,
            'has_archive': month_dir_part + '.zip' in month_files,
            'youtube_link': youtube_link,
            'id': hashlib.md5((song_data.title+song_data.genre.split(', ')[0]+duel).encode()).hexdigest()[:10]

        })

    return songs


def get_youtube_link(month_dir):
    path = os.path.join(month_dir, 'youtube.txt')

    return open(path).read().strip() if os.path.isfile(path) else ''


def parse_artist_links():
    lines = open('artist-links.csv').read().strip().split('\n')

    return {a: l for a, l in [x.split(', ') for x in lines]}

def parse_banner_artist_links():
    lines = open('banner-artist-links.csv').read().strip().split('\n')

    return {a: l for a, l in [x.split(', ') for x in lines]}


def get_deadline_date():
    val = CONFIG['dod_site'].get('deadline_date')

    try:
        date = datetime.date(*[int(x) for x in val.split('-')])
    except (AttributeError, TypeError, ValueError):
        s = 'Error: deadline_date must be of the form YYYY-MM-DD in site.cfg'

        sys.exit(s)

    return date


def set_template_globals():
    now = datetime.datetime.now()
    TEMPLATES.globals['voting'] = VOTING
    TEMPLATES.globals['deadline_date'] = get_deadline_date()
    TEMPLATES.globals['deadline_time'] = DEADLINE_TIME
    TEMPLATES.globals['archive_dir'] = ARCHIVE_DIR
    TEMPLATES.globals['artist_links'] = parse_artist_links()
    TEMPLATES.globals['banner_artist_links'] = parse_banner_artist_links()
    TEMPLATES.globals['songID'] = 1
    TEMPLATES.globals['artistID'] = 1
    TEMPLATES.globals['duelID'] = 1
    TEMPLATES.globals['gameID'] = 1
    TEMPLATES.globals['songArtistID'] = 1
    TEMPLATES.globals['songGameID'] = 1
    TEMPLATES.globals['duelSongID'] = 1
    TEMPLATES.globals['artistDict'] = {}
    TEMPLATES.globals['duelDict'] = {}
    TEMPLATES.globals['gameDict'] = {}
    TEMPLATES.globals['today'] = now.strftime("%Y-%m-%d")




    latest_month = DATA[-1]['month_dir']

    if VOTING:
        _d = lambda d: d['month_dir']

        winners_month = [_d(d) for d in DATA if _d(d) != latest_month][-1]
    else:
        winners_month = latest_month

    winners = [s for s in DATA if s['month_dir'] == winners_month]
    winners.sort(key=lambda s: s['rank'])

    TEMPLATES.globals['latest_duel'] = DATA[-1]['duel']
    TEMPLATES.globals['latest_month'] = latest_month
    TEMPLATES.globals['latest_winners'] = winners

    start_delta = datetime.date.today() - datetime.date(2003, 9, 1)

    TEMPLATES.globals['stats'] = {
        'songs': len(DATA),
        'hours': sum([s['duration'] for s in DATA]) / 60 / 60,
        'years': start_delta.days / 365
    }


def combine_files(files, static_prefix):
    def get_dir(f):
        return os.path.join(TEMPLATE_DIR, 'static', static_prefix, f)

    return '\n'.join([open(get_dir(f)).read() for f in files])


def write_csvs():
    for song in DATA:
        # you are dealing with GLOBAL ids FYI
        if (song['duel'] not in TEMPLATES.globals['duelDict']):
            TEMPLATES.globals['duelDict'][song['duel']] = TEMPLATES.globals['duelID']
            write_duel(song['duel'], song['month_dir'])
        write_duel_song_assoc(TEMPLATES.globals['duelDict'][song['duel']], TEMPLATES.globals['songID'])

        for artist in song['artists']:
            if (artist.lower() not in TEMPLATES.globals['artistDict']):
                TEMPLATES.globals['artistDict'][artist.lower()] = TEMPLATES.globals['artistID']
                link = ""
                if artist in TEMPLATES.globals['artist_links']:
                    link = TEMPLATES.globals['artist_links'][artist]
                write_artist(artist, link)
            write_song_artist_assoc(TEMPLATES.globals['songID'], TEMPLATES.globals['artistDict'][artist.lower()])

        for game in song['games']:
            if (game not in TEMPLATES.globals['gameDict']):
                TEMPLATES.globals['gameDict'][game] = TEMPLATES.globals['gameID']
                write_game(game)
            write_song_game_assoc(TEMPLATES.globals['songID'], TEMPLATES.globals['gameDict'][game])

        write_song(song['title'], song['link'])


def write_song_game_assoc(songID, gameID):
    f = open("song_games.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['songGameID'], songID, gameID, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['songGameID'] += 1
    f.close()

def write_game(title):
    f = open("games.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['gameID'], title, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['gameID'] += 1
    f.close()

def write_song_artist_assoc(songID, artistID):
    f = open("song_artists.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['songArtistID'], songID, artistID, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['songArtistID'] += 1
    f.close()

def write_artist(name, externalLink):
    f = open("artists.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['artistID'], name, externalLink, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['artistID'] += 1
    f.close()

def write_song(title, filename):
    f = open("songs.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['songID'], title, filename, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['songID'] += 1
    f.close()

def write_duel(name, shortName):
    f = open("duels.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['duelID'], name, shortName, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['duelID'] += 1
    f.close()

def write_duel_song_assoc(duelID, songID):
    f = open("duel_songs.csv", "a")
    c = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    c.writerow([TEMPLATES.globals['duelSongID'], duelID, songID, TEMPLATES.globals['today'], None])
    TEMPLATES.globals['duelSongID'] += 1
    f.close()

def build():
    build_data()
    write_csvs()


if __name__ == '__main__':
    if not os.path.isdir(ARCHIVE_DIR):
        sys.exit('Error: `{}` must be in {}'.format(ARCHIVE_DIR, os.getcwd()))

    build()
