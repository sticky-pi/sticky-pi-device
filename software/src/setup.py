from setuptools import setup, find_packages
import os
version = os.environ["SPI_VERSION"]

assert version, "SPI_VERSION must be defined!"
setup(
    name='sticky_pi_device',
    version=version,
    long_description=__doc__,
    packages=find_packages(),
    scripts=['bin/take_picture.py', 'bin/sync_to_harvester.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['rpi_ws281x',
                      'pytz',
                      'netifaces',
                      'pillow',
                      'requests',
                      ###fixme # 'adafruit-circuitpython-dht',
                      'piexif',
                      # 'keyboard',
                      # 'pyserial',
                      #fixme move these to optional dep
                      #'RPi.GPIO',
                      #'picamera'
                      #'Adafruit_DHT', # --install-option="${ADAFRUIT_DHT_OPTION}"
    ]

# export READTHEDOCS=True; pip install picamera # hack to circumvent virtual pi issue
#
# cd /root/os_stub/
# rsync -rvP ./ /
# mkdir /sticky_pi_images
#     extras_require={
#         'remote_api': ['pymysql', 'boto3', 'PyMySQL', 'Flask-HTTPAuth', 'retry'],
#         'test': ['nose', 'pytest', 'pytest-cov', 'codecov', 'coverage'],
#         'docs': ['mock', 'sphinx-autodoc-typehints', 'sphinx', 'sphinx_rtd_theme', 'recommonmark', 'mock']
#     },
#     test_suite='nose.collector'
)
