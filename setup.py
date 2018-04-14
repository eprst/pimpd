try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

classifiers = ['Development Status :: 2 - Pre-Alpha',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: Apache Software License',
               'Intended Audience :: End Users/Desktop',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Multimedia :: Sound/Audio',
               'Topic :: System :: Hardware']

setup(name              = 'pimpd',
      version           = '0.0.1',
      author            = 'Konstantin Sobolev',
      author_email      = 'konstantin.sobolev@gmail.com',
      description       = 'A Python script for controlling MPD on Raspberry Pi with SSD1306-based 128x64 OLED display.',
      license           = 'Apache',
      classifiers       = classifiers,
      url               = 'https://github.com/eprst/pimpd',
      dependency_links  = [
          'https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5',
          'https://github.com/adafruit/Adafruit_Python_SSD1306/tarball/master#egg=Adafruit-SSD1306-1.6.1',
      ],
      install_requires  = ['Adafruit-GPIO>=0.6.5','Adafruit_SSD1306>=1.6.1'],
      packages          = find_packages())