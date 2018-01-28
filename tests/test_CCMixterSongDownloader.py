import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ccmixter_song_downloader.__main__ import CCMixterSongDownloader

from pprint import pprint

downloads_folder = os.path.join(os.path.dirname(__file__), 'tmp_dl')


def setup_function(function):
    if not os.path.isdir(downloads_folder):
        os.makedirs(downloads_folder)
    return function


def teardown_function(function):
    function()
    for file in os.listdir(downloads_folder):
        os.remove(os.path.join(downloads_folder, file))
    os.rmdir(downloads_folder)
    assert True


@teardown_function
@setup_function
def test_case1():
    dl = CCMixterSongDownloader()
    dl.download(save_folder=downloads_folder, tags='', limit=1)
    pprint(dl.songs_metadata)
    assert len(os.listdir(downloads_folder)) == 2  # .mp3 & history text file
