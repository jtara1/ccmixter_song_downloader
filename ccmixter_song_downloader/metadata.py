import collections


class SongMetadata(collections.MutableMapping):
    def __init__(self, artist='N/A', name='N/A', length=0.0, link='N/A',
                 license_url='N/A', license='N/A'):
        """Contains metadata needed for CCMixterSongDownloader usable
        as a dictionary. All arguments are strings exception length is
        a float
        Example:

        {'artist': 'Aussens@iter',
         'length': 241.162,
         'license': 'CC BY 3.0',
         'license_url': 'http://creativecommons.org/licenses/by/3.0/',
         'link': 'http://ccmixter.org/files/tobias_weber/57249',
         'name': 'Event Horizon'}

        """
        self.dict = dict()
        self.update(artist=artist, name=name, length=length, link=link,
                    license_url=license_url, license=license)

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __delitem__(self, key):
        del self.dict[key]

    def __iter__(self):
        return iter(self.dict)

    def __len__(self):
        return len(self.dict)

    def __str__(self):
        return str(self.dict)


if __name__ == '__main__':
    m = SongMetadata(
        artist='neat band', name='james', length=100.2,
        link='https://google.com',
        license_url='http://creativecommons.org/licenses/by/3.0/',
        license='CC BY 3.0')
    print(m)
    print(m['license'])
