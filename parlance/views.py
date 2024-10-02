# parlance.views
# Site level views and pages not associated with a specific app.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 21:17:47 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: views.py [] benjamin@rotational.io $

"""
Site level views and pages not associated with a specific app.
"""

##########################################################################
## Imports
##########################################################################

from django.views.generic import TemplateView


class Dashboard(TemplateView):

    template_name = "site/dashboard.html"
