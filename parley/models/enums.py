# parley.models.enums
# Enum constants for use as model choices to simplify enum management.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Sat Oct 05 15:45:20 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: enums.py [] benjamin@rotational.io $

"""
Enum constants for use as model choices to simplify enum management.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from django.utils.translation import gettext_lazy as _


class SimilarityMetric(models.TextChoices):
    """
    Similarity metrics define the automated comparisons between an LLM response and the
    expected output as defined by the prompt.
    """

    COSINE_TFIDF = ("csti", _("Cosine TF-IDF"))
    COSINE_TF = ("cstf", _("Cosine Term Frequency"))
    JACCARD = ("jacc", _("Jaccard"))
    WORD2VEC = ("w2vc", _("Cosine of Word2Vec Average"))
    GLOVE = ("glve", _("Cosine of GloVe Average"))
    FAST = ("fast", _("Cosine of FastText Average"))
    DOC2VEC = ("d2vc", _("Cosine of Doc2Vec"))
    BERT = ("bert", _("Cosine of BERT"))


class OutputFormat(models.TextChoices):
    """
    OutputFormat indicates the expected serialized response from an LLM to a prompt.
    By default, this is usually just simple text, but LLMs and generative AI can also
    produce JSON, XML, CSV data or even images or data visualizations.
    """

    TEXT = ("text", _("text"))
    JSON = ("json", _("JSON"))
    XML = ("xml", _("XML"))
    CSV = ("csv", _("CSV"))
    IMAGE = ("img", _("image"))
    DATA_VIZ = ("dviz", _("Data Visualization"))


class FivePointLikert(models.IntegerChoices):
    """
    FivePointLikert is a standard 5-point Likert scale for user evaluations, where 1 is
    strongly disagree and 5 is strongly agree.
    """

    STRONGLY_DISAGREE = (1, _("Strongly Disagree"))
    DISAGREE = (2, _("Disagree"))
    NEUTRAL = (3, _("Neutral"))
    AGREE = (4, _("Agree"))
    STRONGLY_AGREE = (5, _("Strongly Agree"))
