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
    def run():
        function()
        for file in os.listdir(downloads_folder):
            os.remove(os.path.join(downloads_folder, file))
        os.rmdir(downloads_folder)
    return run


def clean_up_old(function):
    if os.path.isdir(downloads_folder):
        for file in os.listdir(downloads_folder):
            os.remove(os.path.join(downloads_folder, file))
        os.rmdir(downloads_folder)
    return function


@setup_function
# @clean_up_old
def test_case1():
    """test_case1 = teardown_function(setup_function(test_case1)))"""
    dl = CCMixterSongDownloader()
    dl.download(save_folder=downloads_folder, tags='', limit=2,
                skip_previous_songs=True)
    assert len(os.listdir(downloads_folder)) >= 2  # .mp3 & history text file
    pprint([str(metadata) for metadata in dl.songs_metadata], width=68)
    # print(dl.songs_metadata[0])


if __name__ == '__main__':
    test_case1()
