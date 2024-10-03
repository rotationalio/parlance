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

from django.shortcuts import render
from django.views.generic import TemplateView


##########################################################################
## Views
##########################################################################

class Dashboard(TemplateView):

    template_name = "site/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_id'] = "dashboard"
        return context


##########################################################################
## Error Views
##########################################################################


def server_error(request, **kwargs):
    return render(request, template_name="errors/500.html", status=500)


def not_found(request, exception, **kwargs):
    return render(request, template_name="errors/404.html", status=404)


def permission_denied(request, exception, **kwargs):
    return render(request, template_name="errors/403.html", status=403)


def bad_request(request, exception, **kwargs):
    return render(request, template_name="errors/400.html", status=400)
