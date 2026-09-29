class repo_ingestError(Exception):
    """Base class for all expected errors."""


class InvalidSourceError(repo_ingestError):
    """The source is not a valid/allowed local path or repository URL."""


class CloneError(repo_ingestError):
    """`git` failed (missing binary, auth failure, timeout, bad branch...)."""


class SubpathError(repo_ingestError):
    """The requested sub-directory does not exist or is not a directory."""
