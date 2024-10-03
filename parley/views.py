# parley.views
# Parley views and controllers.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 17:59:43 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: views.py [] benjamin@rotational.io $

"""
Parley views and controllers.
"""

##########################################################################
## Imports
##########################################################################

from django.views.generic.edit import FormView
from parley.forms import Uploader


##########################################################################
## Views
##########################################################################

class UploaderFormView(FormView):

    ready = False
    template_name = "upload.html"
    form_class = Uploader

    def form_valid(self, form):
        if not self.ready:
            raise Exception("not implemented yet")
        return super().form_valid(form)

    def form_invalid(self, form):
        if not self.ready:
            raise Exception("form invalid")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "upload"
        return context
