from django.db.models import Func


class FuncDateUTC(Func):
    function = 'DATE'
    template = "%(function)s(%(expressions)s AT TIME ZONE 'UTC')"
