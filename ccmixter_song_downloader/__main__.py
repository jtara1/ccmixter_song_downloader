import requests
from bs4 import BeautifulSoup
import os
import get_media_files

try:  # python 3
    from urllib.parse import quote, unquote
except ImportError:  # python 2
    from urllib import quote, unquote

from ccmixter_song_downloader.history_manager import History
from ccmixter_song_downloader.general_utility import slugify
from ccmixter_song_downloader.metadata import SongMetadata


class CCMixterSongDownloader:
    # needs: tags, sort, limit, offset, reversed
    # check this for valid values http://ccmixter.org/query-api
    url_template = 'http://ccmixter.org/api/query?tags={tags}&sort={sort}&' \
                   'limit={limit}&offset={offset}&' \
                   'sinced=1/1/2003&ord={reversed}'

    def __init__(self):
        # e.g.: {'song': 's name', 'artist': 'john', 'website': 'ccMixter.org'
        # 'file': '/home/user/s\ name.mp3'}
        self.songs_metadata = []

    def download(self, save_folder, tags='classical', sort='date', limit=1,
                 reversed=False, skip_previous_songs=True):
        """Downloads songs from ccMixter and saves them

        :param save_folder: location of saved music files
        :param tags: <string> in url, tags of songs used as a filter
        :param sort: <string> in url, sort type used to filter songs
        :param limit: <int> amount of songs to download before stopping
        :param skip_previous_songs: <boolean> if true, checks for previous \n
            queries made and skips the amount downloaded (as offset in url \n
            query filter).
        :return:
        """
        # location of music files downloaded
        save_folder = os.path.abspath(save_folder)

        if not skip_previous_songs:
            offset = 0
        else:
            _, offset = History.get_previous_download_amount(tags, sort,
                                                             save_folder)

        query_url = self.url_template.format(
            tags=tags, sort=sort, limit=limit, offset=offset,
            reversed='ASC' if reversed else 'DESC')

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

            file_name = tag['about']
            # avoid downloading zip files
            if file_name.endswith(('.zip', '.zip ')):
                limit += 1
                continue

            # convert URL text elements (%2D -> '-')
            # and make it valid file name
            file_name = slugify(unquote(file_name))
            save_path = os.path.join(save_folder, file_name)
            print('[CCMixterSongDownloader] Saving: {} as {}'
                  .format(tag['about'], save_path))

            # download the song
            CCMixterSongDownloader._direct_link_download(
                tag['about'].strip(),
                save_path)

            # get length of song
            song_media = get_media_files.GetMediaFiles(save_path)
            length = song_media.files[0][1]['Audio']['duration'] / 1000

            # keep info of the song
            artist, song, link = self._get_info_from_tag(tag)
            metadata = SongMetadata(length=length, artist=artist, name=song,
                                    link=link)
            self.songs_metadata.append(metadata)


        if count + 1 < limit:
            print('[CCMixterSongDownloader] WARNING: Downloaded {} songs when '
                  'limit = {}'.format(count, limit))

        log_file_path = os.path.join(save_folder, History.log_file)
        History.history_log(log_file=log_file_path,
                            mode='write',
                            write_data=self._create_history_log_info(
                                tags, sort, limit))

    def _get_info_from_tag(self, tag):
        """Extracts info about the song from the HTML tag (with
        class='upload_info')
        Appends the download_info attr to hold the info of the song in a dict

        :param tag: (bs4 Tag object) the HTML tag with class='upload_info'
        """
        title_tag = tag.find('a', attrs={'property': 'dc:title'})
        link = title_tag['href']
        song = title_tag.text
        artist = tag.find('a', attrs={'property': 'dc:creator'}).text
        return artist, song, link
        # self.download_info.append({'website': link, 'song': song,
        #                            'artist': artist})

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
    def _create_history_log_info(tags, sort, downloads):
        """Info stored when downloading complete to help skip songs already
        downloaded for future calls to download method.
        e.g.: {'classical+hip_hop': {'date': {'downloads': 10}}}
        """
        return {tags: {sort: {'downloads': downloads}}}


if __name__ == '__main__':
    # test
    dl = CCMixterSongDownloader()
    dl.download('tmp_downloads')
