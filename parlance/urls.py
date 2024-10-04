# parlance.urls
# Defines all of the routes and associated views with the urls for the app.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 21:19:17 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: urls.py [] benjamin@rotational.io $

"""
URL configuration for parlance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from django.urls import path, include

from parley.views import UploaderFormView
from parlance.views import Dashboard, AccountSettings, AccountProfile


##########################################################################
## URL Patterns
##########################################################################

urlpatterns = [
    # Application Pages
    path("", Dashboard.as_view(), name="dashboard"),
    path("upload/", UploaderFormView.as_view(), name="upload"),
    path("account/profile", AccountProfile.as_view(), name="account-profile"),
    path("account/settings", AccountSettings.as_view(), name="account-settings"),
    # Admin URLs
    path("admin/", admin.site.urls),
    # Authentication URLs
    path("accounts/", include("django.contrib.auth.urls")),
]


##########################################################################
## Error handling
##########################################################################

handler400 = "parlance.views.bad_request"
handler403 = "parlance.views.permission_denied"
handler404 = "parlance.views.not_found"
handler500 = "parlance.views.server_error"
