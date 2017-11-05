import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join("../", __file__)))
from CCMixterSongDownloader import CCMixterSongDownloader


def test_case1():
    folder = os.path.join(__file__, 'tmp_dl')
    dl = CCMixterSongDownloader()
    dl.download(save_folder=folder, tags='classical', limit=2)
    print(dl.download_info)
    assert True
