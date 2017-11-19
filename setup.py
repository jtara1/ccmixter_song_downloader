from distutils.core import setup
import re


def get_install_requirements():
    requirements = []
    with open('requirements.txt', 'r') as f:
        for line in f:
            requirements.append(re.sub("\s", "", line))
    print(requirements)
    return requirements

if __name__ == "__main__":
    pass

setup(name='CCMixterSongDownloader',
      version='v0.1',
      description='Download songs from ccMixter',
      author='James T',
      author_email='jtara@tuta.io',
      url='https://github.com/jtara1/CCMixterSongDownloader',
      install_requires=get_install_requirements(),
      )
