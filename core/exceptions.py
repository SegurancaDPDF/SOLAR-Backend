class CoreBaseException(Exception):
    message = ''

    # TODO: Verificar necessidade da sobrescrita do Exception
    def __init__(self, msg=None, *args, **kwargs):
        msg = msg or self.message
        super().__init__(msg, *args, **kwargs)
