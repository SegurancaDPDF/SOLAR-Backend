# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip
import six


def int_or_none(value):
    if value and (
        value is not None and (
            isinstance(value, six.text_type) and 'none' not in value.lower()
            )
    ):
        return int(value)
