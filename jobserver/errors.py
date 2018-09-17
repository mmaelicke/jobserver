class JobserverError(Exception):
    pass

class JobExecutionRestrictedError(RuntimeError, JobserverError):
    pass