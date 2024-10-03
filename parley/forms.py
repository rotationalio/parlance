# parley.forms
# Forms for handling and validating user input.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Wed Oct 02 14:04:48 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: forms.py [] benjamin@rotational.io $

"""
Forms for handling and validating user input.
"""

##########################################################################
## Imports
##########################################################################

from django import forms


class Uploader(forms.Form):

    jsonl = forms.FileField(allow_empty_file=False)
