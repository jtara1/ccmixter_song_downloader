import collections


class SongMetadata(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, artist='N/A', name='N/A', length=0.0, link='N/A'):
        self.dict = dict()
        self.update(artist=artist, name=name, length=length, link=link)

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
    m = SongMetadata(artist='neat band', name='james', length=100.2)
    print(m)
