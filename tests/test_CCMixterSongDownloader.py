from os.path import join
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ccmixter_song_downloader.__main__ import CCMixterSongDownloader
from ccmixter_song_downloader.history_manager import History

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
    dl.download(save_folder=downloads_folder, tags='', limit=3, reverse=True,
                skip_previous_songs=True)
    dl.download(save_folder=downloads_folder, tags='rap', limit=1,
                reverse=True, skip_previous_songs=True)
    assert len(os.listdir(downloads_folder)) >= 2  # .mp3 & history text file
    pprint([dict(metadata) for metadata in dl.songs_metadata], width=68)
    # print(dl.songs_metadata[0])


def test_history_log():
    log_path = join(downloads_folder, History.log_file)
    with open(log_path, 'r') as f:
        data = json.load(f)
    assert(data == {'': {'date': {'downloads': 3}},
                    'rap': {'date': {'downloads': 1}}})


if __name__ == '__main__':
    test_case1()
