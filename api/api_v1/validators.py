# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from datetime import date, datetime, time
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class NumeroAtendimentoValidator(RegexValidator):
    regex = r'^\d{12}$'


def date_is_after_tomorrow(value, now=timezone.now):
    """
    Raises if value is a date before after tomorrow.

    Example:

    now = datetime(2018, 01, 01, 23, 59, 59)
    today = date(2018, 01, 01)

    tomorrow = date(2018, 01, 02)
    after_tomorrow = date(2018, 01, 03)

    date_is_after_tomorrow(after_tomorrow, lambda: now) is None  # valido.

    #The bellow should raise ValidationError:

    date_is_after_tomorrow(now, lambda: now)
    date_is_after_tomorrow(today, lambda: now)
    date_is_after_tomorrow(tomorrow, lambda: now)
    """

    if not isinstance(value, (datetime, date)):
        raise ValidationError(
            _("The value entered isn't a valid type of date or datetime.")
        )

    now_ = now()
    today = now_.date()
    today = datetime.combine(today, time.min)

    tomorrow = today + timezone.timedelta(days=1)
    if not isinstance(value, datetime):
        value = datetime.combine(value, time.min)

    # TODO: Lembrar de tratar caso em que value contem datetime com informacao de timezone
    if value < tomorrow:
        raise ValidationError(
            _("The date entered must be greater or equal than after tomorrow")
        )
