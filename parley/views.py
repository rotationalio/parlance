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

from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic.edit import FormView

from parley.forms import Uploader
from parley.exceptions import ParlanceUploadError


##########################################################################
## Views
##########################################################################

class UploaderFormView(FormView):

    template_name = "upload.html"
    form_class = Uploader
    success_url = reverse_lazy("upload")

    def form_valid(self, form):
        # Handle the uploaded data stored in the form
        try:
            counts = form.handle_upload()
        except ParlanceUploadError as e:
            # If an error occurs, stop processing and show the error to the user.
            form.add_error(None, str(e))
            return self.form_invalid(form)

        # Create the success message with the counts
        messages.success(self.request, mark_safe(counts.html()))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_id"] = "upload"
        return context

    @transaction.atomic
    def post(self, *args, **kwargs):
        """
        Ensures that all database operations during a request are all or nothing.
        """
        return super().post(*args, **kwargs)
