# parlance.version
# Helper module for managing versioning information
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 14:56:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: __init__.py [] benjamin@rotational.io $

"""
Helper module for managing versioning information
"""

##########################################################################
## Imports
##########################################################################

import os
import subprocess


## Commit environment variables
SLUG_COMMIT_ENV = [
    "GIT_REVISION", "HEROKU_SLUG_COMMIT", "SLUG_COMMIT",
]


##########################################################################
## Versioning
##########################################################################

__version_info__ = {
    'major': 0,
    'minor': 5,
    'micro': 0,
    'releaselevel': 'alpha',
    'serial': 6,
}


def get_version(short=False, revision=False):
    """
    Returns the version from the version info.
    """
    if __version_info__['releaselevel'] not in ('alpha', 'beta', 'final'):
        raise ValueError(
            "unknown release level '{}', select alpha, beta, or final.".format(
                __version_info__['releaselevel']
            )
        )

    vers = ["{major}.{minor}.{micro}".format(**__version_info__)]

    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('{}{}'.format(__version_info__['releaselevel'][0],
                                  __version_info__['serial']))

    if revision:
        vers.append("@{}".format(get_revision(short=short)))

    return ''.join(vers)


def get_revision(short=False, env=True):
    """
    Returns the latest git revision (sha1 hash).
    """

    # First look up the revision from the environment
    if env:
        for envvar in SLUG_COMMIT_ENV:
            if envvar in os.environ:
                slug = os.environ[envvar]
                if short:
                    return slug[:7]
                return slug

    # Otherwise return the subprocess lookup of the revision
    cmd = ['git', 'rev-parse', 'HEAD']
    if short:
        cmd.insert(2, '--short')

    return subprocess.check_output(cmd).decode('utf-8').strip()


def get_sentry_release():
    return "parlance v{}".format(get_version(short="True", revision=True))
