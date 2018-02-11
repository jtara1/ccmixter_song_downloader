from os.path import join, dirname
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ccmixter_song_downloader.__main__ import CCMixterSongDownloader
from ccmixter_song_downloader.history_manager import History
from ccmixter_song_downloader.metadata import SongMetadata

import json
from pprint import pprint

downloads_folder = os.path.join(os.path.dirname(__file__), 'tmp_dl')


def setup_func(func):
    if not os.path.isdir(downloads_folder):
        os.makedirs(downloads_folder)
    return func


def clean_up_old(func):
    if os.path.isdir(downloads_folder):
        for file in os.listdir(downloads_folder):
            os.remove(os.path.join(downloads_folder, file))
        os.rmdir(downloads_folder)
    return func


@setup_func
@clean_up_old
def test_case1():
    """test_case1 = teardown_function(setup_function(test_case1)))"""
    dl = CCMixterSongDownloader()
    data = dl.download(save_folder=downloads_folder, tags='', limit=3,
                       reverse=True, skip_previous_songs=True)
    data2 = dl.download(save_folder=downloads_folder, tags='female_vocals',
                        limit=1,
                        reverse=True, skip_previous_songs=True)
    data.update(data2)
    assert len(os.listdir(downloads_folder)) >= 2  # .mp3 & history text file
    pprint(data)


def test_history_log():
    log_path = join(downloads_folder, History.log_file)
    with open(log_path, 'r') as f:
        data = json.load(f)
    assert(data == {'': {'date': {'downloads': 3}},
                    'rap': {'date': {'downloads': 1}}})


def test_metadata():
    expected = {
        "stab_-_Backtrace.mp3":
        {
            "length": 283.689,
            "direct_link":
                "http://ccmixter.org/content/stab/stab_%2D_Backtrace.mp3 ",
            "name": "Backtrace",
            "license": "CC BY 2.5",
            "license_url": "http://creativecommons.org/licenses/by/2.5/",
            "artist": "Stab",
            "link": "http://ccmixter.org/files/stab/3067"
        },
        "melquiades_-_Brahms_Intermezzo_116.4.mp3":
        {
            "length": 280.084,
            "direct_link":
                "http://ccmixter.org/content/melquiades/melquiades_%2D_Brahms_Intermezzo_116.4.mp3 ",
            "name": "Brahms Intermezzo 116.4",
            "license": "CC BY 2.5",
            "artist": "melquiades",
            "license_url": "http://creativecommons.org/licenses/by/2.5/",
            "link": "http://ccmixter.org/files/melquiades/2995"
        }
    }
    data = CCMixterSongDownloader.deserialize(dirname(__file__))
    pprint(data)
    assert(data == expected)


if __name__ == '__main__':
    test_case1()
