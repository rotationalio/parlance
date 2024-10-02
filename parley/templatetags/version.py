# parley.templatetags.version
# Adds version information to the page.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 21:52:22 2024 -0500
#
# ID: version.py [] benjamin@bengfort.com $

"""
Adds version information to the page.

TODO: move to parlance specific app when created.
"""

##########################################################################
## Imports
##########################################################################

from parlance import get_version
from django import template

register = template.Library()


##########################################################################
## Template Tags
##########################################################################


@register.simple_tag()
def version():
    return get_version(short=True, revision=False)
