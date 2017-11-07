import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from CCMixterSongDownloader.download_music import CCMixterSongDownloader


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
    dl.download(save_folder=downloads_folder, tags='classical', limit=1)
    print(dl.download_info)
    assert len(os.listdir(downloads_folder)) == 2  # .mp3 & history text file
