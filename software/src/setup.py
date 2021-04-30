from setuptools import setup, find_packages
import os
exec(open('sticky_pi_device/_version.py').read())

assert __version__, "SPI_VERSION must be defined!"
setup(
    name='sticky_pi_device',
    version=__version__,
    long_description=__doc__,
    packages=find_packages(),
    scripts=['bin/take_picture.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['rpi_ws281x',
                      'pytz',
                      'netifaces',
                      'requests',
                      'piexif',
    ],
    extras_require={
        ###Not needed : # 'adafruit-circuitpython-dht',
        'device': ['pyserial',
                  'RPi.GPIO',
                  'picamera',
                  'Adafruit_DHT'],
        'devel': ['pillow']
#         'test': ['nose', 'pytest', 'pytest-cov', 'codecov', 'coverage'],
#         'docs': ['mock', 'sphinx-autodoc-typehints', 'sphinx', 'sphinx_rtd_theme', 'recommonmark', 'mock']
    },
#     test_suite='nose.collector'
)
