import sys
import requests
from bs4 import BeautifulSoup
import os
from os.path import basename, dirname
from get_media_files import GetMediaFiles
import logging
from logging import Formatter, StreamHandler

try:  # python 3
    from urllib.parse import quote, unquote
except ImportError:  # python 2
    from urllib import quote, unquote

from ccmixter_song_downloader.history_manager import History
from ccmixter_song_downloader.general_utility import slugify
from ccmixter_song_downloader.metadata import SongMetadata


class CCMixterSongDownloader:
    # needs: tags, sort, limit, offset, reverse, license
    # check this for valid values http://ccmixter.org/query-api
    URL_TEMPLATE = 'http://ccmixter.org/api/query?tags={tags}&sort={sort}&' \
                   'limit={limit}&offset={offset}&' \
                   'sinced=1/1/2003&ord={reverse}&lic={license}'
    # JSON file contains metadata of each song downloaded
    CCMIXTER_METADATA = '_ccmixter_metadata.json'

    def __init__(self):
        """Wrapper class for creating an HTTP query for ccmixter.org to
        download songs
        Example:
            # get the 5 oldest classical CC-BY licensed songs
            dl = CCMixterSongDownloader()
            dl.download(
                save_folder='downloads/', tags='classical', sort='date',
                limit=5, reverse=True, license='by')

            # the following query would then be generated
            # http://ccmixter.org/api/query?tags=classical&limit=5&offset=0&sinced=1/1/2003&ord=ASC&lic=by
            # and download 5 songs

        """
        self.log = logging.getLogger(__class__.__name__)
        handler = StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(Formatter("[%(name)s] %(levelname)s %(asctime)s "
                                       "%(message)s"))
        self.log.addHandler(handler)

        # at index 0 is info of 1st song downloaded, index 0 is 2nd song, etc
        self.songs_metadata = []

    def download(self, save_folder, tags='classical', sort='date', limit=1,
                 reverse=False, license='by', skip_previous_songs=True):
        """Downloads songs from ccMixter and saves them. All arguments
        exception save_folder and skip_previous_songs are used for
        building the query

        :param save_folder: location of saved music files
        :param tags: <str> in url, tags of songs used as a filter
        :param sort: <str> in url, sort type used to filter songs
        :param limit: <int> amount of songs to download before stopping
        :param reverse: <bool> reverses the order in which the \n
            list of songs are returned from ccmixter
        :param license: <str> the type of matching license of songs \n
            for query building
        :param skip_previous_songs: <bool> if true, checks for previous \n
            queries made and skips the amount downloaded (as offset in url \n
            query filter).
        :return:
        """
        # location of music files downloaded
        save_folder = os.path.abspath(save_folder)

        if not skip_previous_songs:
            history_data = {}
            offset = 0
        else:
            history_data, offset = History.get_previous_download_amount(
                tags, sort, save_folder)

        query_url = self.URL_TEMPLATE.format(
            tags=tags, sort=sort, limit=limit, offset=offset,
            reverse='ASC' if reverse else 'DESC', license=license)
        self.log.debug("Query created: {}".format(query_url))
        response = requests.get(query_url)
        soup = BeautifulSoup(response.text, 'lxml')

        count = 0
        # iterate over the HTML <div> tag that contains the direct link to .mp3
        for count, tag in enumerate(
                soup.find_all('div', attrs={'class': 'upload_info'}),
                start=0):

            # we've downloaded enough songs to reach the limit
            if count >= limit:
                break

            direct_link = tag['about']
            # avoid downloading zip files
            if direct_link.endswith(('.zip', '.zip ')):
                # limit += 1
                count -= 1
                continue

            # convert URL text elements (%2D -> '-')
            # and make it valid file name
            file_name = slugify(basename(unquote(direct_link)))
            save_path = os.path.join(save_folder, file_name)
            self.log.info('Saving: {} as {}'
                          .format(tag['about'], save_path))

            # download the song
            CCMixterSongDownloader._direct_link_download(
                tag['about'].strip(),
                save_path)

            # get length of song
            files = GetMediaFiles(save_path).get_info()
            length = files[0][1]['Audio']['duration']
            if length:  # length is occasionally None
                length /= 1000
            else:
                if length == '':
                    length = '""'
                self.log.critical('{} HAS LENGTH OF {}'
                                  .format(save_path, length))

            # keep info of the song
            artist, song, link, lic, lic_url = self._parse_info_from_tag(tag)
            metadata = SongMetadata(
                length=length, artist=artist, name=song, link=link,
                license_url=lic_url, license=lic, direct_link=direct_link)
            self.songs_metadata.append(metadata)

            # update metadata in file with new song downloaded
            History.history_log(
                wdir=save_folder, log_file=self.CCMIXTER_METADATA,
                mode='update',
                write_data=self._create_metadata_serialization_data(
                    file_name, metadata))

        if count + 1 < limit:
            self.log.warning('Downloaded {} songs when limit = {}'
                             .format(count, limit))

        History.history_log(wdir=save_folder,
                            log_file=History.log_file,
                            mode='write',
                            write_data=self._create_history_log_info(
                                history_data, tags, sort, limit))

    def _parse_info_from_tag(self, tag):
        """Extracts info about the song from the HTML tag (with
        class='upload_info')
        Appends the download_info attr to hold the info of
        the song in a dict

        :param tag: <bs4.element.Tag> the HTML tag with \n
        class='upload_info'
        """
        title_tag = tag.find('a', attrs={'property': 'dc:title'})
        link = title_tag['href']
        song = title_tag.text
        artist = tag.find('a', attrs={'property': 'dc:creator'}).text
        license_tag = tag.find('a', attrs={'class': 'lic_link'})
        license_url = license_tag['href']

        return artist, song, link, \
            self._parse_cc_license_from_url(license_url), license_url

    @staticmethod
    def _direct_link_download(url, full_save_path):
        """Saves the content from a URL that points directly to media

        :param url: (string) URL of the link whose content will be saved locally
        :param full_save_path: (string) local file path (with the file name)
        :return: 1 if url opened successfully, 0 otherwise
        """
        base_path = os.path.dirname(full_save_path)
        if not os.path.isdir(base_path):
            os.makedirs(base_path)

        r = requests.get(url)
        if r.ok:
            with open(full_save_path, 'wb') as f:
                f.write(r.content)
            return 1
        else:
            r.raise_for_status()
            return 0

    @staticmethod
    def _create_history_log_info(previous_history, tags, sort, downloads):
        """Info stored when downloading complete to help skip songs already
        downloaded for future calls to download method.
        e.g.: {'classical+hip_hop': {'date': {'downloads': 10}}}
        """
        previous_history.update(
            {tags: {sort: {'downloads': downloads}}})
        return previous_history

    @staticmethod
    def _parse_cc_license_from_url(url):
        """url should look like
        http://creativecommons.org/licenses/by/3.0/
        """
        # rm last "/" character, split by "/" characters
        url = url[:-1].split('/')
        number, cc_license = url[-1], url[-2]
        return "CC {} {}".format(cc_license.upper(), number)

    @staticmethod
    def _create_metadata_serialization_data(file_name, song_metadata):
        return {file_name: dict(song_metadata)}


if __name__ == '__main__':
    # test
    dl = CCMixterSongDownloader()
    dl.download('tmp_downloads')
