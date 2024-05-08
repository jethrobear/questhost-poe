from django.core.management.base import CommandError

class PTouchNotFoundError(CommandError):
    pass

class PTouchAccessError(CommandError):
    pass

class PTouchBusyError(CommandError):
    pass