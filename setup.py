"""Based on: https://github.com/pypa/sampleproject."""
from os import path
from setuptools import find_packages, setup

# Get the long description from the README file
with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

TESTS_REQUIRE = ['pylint', 'pytest', 'pytest-pylint']
setup(
    name='telegram_voice_to_text',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='Telegram voice to text bot.',
    long_description=long_description,

    url='https://github.com/tiagoshibata/telegram-voice-to-text',

    author='Tiago Koji Castro Shibata',
    author_email='tiago.shibata@gmail.org',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
    ],

    keywords='bot',

    packages=find_packages(),

    install_requires=['clarifai', 'google-cloud-language', 'google-cloud-speech', 'Pillow', 'pytesseract', 'python-telegram-bot', 'scipy'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': TESTS_REQUIRE,
    },

    setup_requires=['pytest-runner'],

    tests_require=TESTS_REQUIRE,

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={},
)
