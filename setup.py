from setuptools import setup, find_packages
import sys, os

setup(
    name                  = 'cherrytile',
    version               = '0.1',
    description           = "Caching tile server implemented with cherrypy",
    long_description      = "cherrytile leverages both cherrypy to \
                            provide one with a modern, persistent, performant \
                            tile caching server build around mapnik.",
    classifiers           = [], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords              = 'rest osm cherrypy',
    author                = 'bordicon',
    author_email          = 'pandazero@gmail.com',
    url                   = 'http://github.com/bordicon/cherrytile',
    license               = 'apache',
    packages              = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data  = True,
    zip_safe              = False,
    install_requires      = [ 'mapnik2', 'redis-py', 'cherrypy' ],
    entry_points          = """ # -*- Entry points: -*- """,
    scripts               = ['bin/cherrytile-server'])
