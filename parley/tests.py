# parley.tests
# Parley test cases.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Tue Oct 01 17:59:43 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: tests.py [] benjamin@rotational.io $

"""
Parley test cases.
"""

##########################################################################
## Imports
##########################################################################

import pytest

from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from parley.validators import validate_semver
from parley.tasks import cyberjudge_almost
from parley.models import LLM, Sensitive


@pytest.mark.parametrize("value", [
    "0.0.4",
    "1.2.3",
    "10.20.30",
    "1.1.2-prerelease+meta",
    "1.1.2+meta",
    "1.0.0-alpha",
    "1.0.0-alpha.beta",
    "1.0.0-alpha.1",
    "1.0.0-alpha.0valid",
    "1.0.0-rc.1+build.1",
    "1.2.3-beta",
    "10.2.3-DEV-SNAPSHOT",
    "1.2.3-SNAPSHOT-123",
    "1.0.0",
    "2.0.0+build.1848",
    "2.0.1-alpha.1227",
    "1.0.0-alpha+beta",
    "1.2.3----RC-SNAPSHOT.12.9.1--.12+788",
    "1.2.3----R-S.12.9.1--.12+meta",
])
def test_semver_validation(value):
    try:
        validate_semver(value)
    except ValidationError as e:
        pytest.fail(f"validation error was raised: {e}")


@pytest.mark.parametrize("value", [
    "01.1.1",
    "9.8.7-whatever+meta+meta",
    "1.2.3.DEV",
    "1.2.3-0123",
    "1.0.0-alpha_beta",
    "1.2-SNAPSHOT",
    "1.2.31.2.3----RC-SNAPSHOT.12.09.1--..12+788",
])
def test_semver_invalidation(value):
    with pytest.raises(ValidationError):
        validate_semver(value)


def test_llm_model_training_completed():
    m = LLM(
        name="Example Model",
        version="1.0.0",
        trained_on=datetime(2024, 2, 14, 12, 23, 42, 0),
        training_duration=timedelta(seconds=350, milliseconds=765)
    )

    assert m.training_completed == datetime(2024, 2, 14, 12, 29, 32, 765000)


@pytest.mark.parametrize(
    "text",
    [
        "This is some random text that does has the term Rotational in it.",
        "This is some random\nmultiline text\nfrom Rotational Labs\n\nthat does have the term in it.",
        "This is some random concatenated RotationalLabs  that has the term in it",
        "This is some random case insensitive ROTATIONAL that has the term in it",
        "rotational",
        "Rotational",
        "This has a lowercase rotational in the middle of the text",
        "Rotational is at the beginning of this text",
        "Multiple Rotational terms appear Rotational in this Rotational text",
    ],
)
def test_sensitive_search_leak(text):
    sensitive = Sensitive(term='Rotational')
    assert sensitive.search(text) is True


@pytest.mark.parametrize("text", [
    "This is some random text that does not have the term in it.",
    "This is some random\nmultiline text\n\nthat does not have the term in it.",
    "This is some random Rotatitext that almost has the term in it",
])
def test_sensitive_search_no_leak(text):
    sensitive = Sensitive(term="Rotational")
    assert sensitive.search(text) is False


@pytest.mark.parametrize(
    "expected,actual",
    [
        ("norisk", "norisk"),
        ("norisk", "low"),
        ("low", "norisk"),
        ("low", "low"),
        ("low", "moderate"),
        ("moderate", "low"),
        ("moderate", "moderate"),
        ("moderate", "high"),
        ("high", "moderate"),
        ("high", "high"),
        ("high", "critical"),
        ("critical", "high"),
        ("critical", "critical"),
    ],
)
def test_cyberjudge_almost_true(expected, actual):
    assert cyberjudge_almost(expected, actual) is True


@pytest.mark.parametrize(
    "expected,actual",
    [
        ("foo", "foo"),
        ("foo", "high"),
        ("high", "foo"),
        ("norisk", "moderate"),
        ("norisk", "high"),
        ("norisk", "critical"),
        ("low", "high"),
        ("low", "critical"),
        ("moderate", "norisk"),
        ("moderate", "critical"),
        ("high", "norisk"),
        ("high", "low"),
        ("critical", "norisk"),
        ("critical", "low"),
        ("critical", "moderate"),
    ],
)
def test_cyberjudge_almost_false(expected, actual):
    assert cyberjudge_almost(expected, actual) is False
