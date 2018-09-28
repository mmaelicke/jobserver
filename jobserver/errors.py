class JobserverError(Exception):
    pass


class JobExecutionRestrictedError(RuntimeError, JobserverError):
    pass


class CodeBlockMissingError(AttributeError, JobserverError):
    pass


class DisabledError(ValueError, JobserverError):
    pass