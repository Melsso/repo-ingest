class RepoIngestError(Exception):
    """Base class for all expected errors."""


class InvalidSourceError(RepoIngestError):
    """The source is not a valid/allowed local path or repository URL."""


class CloneError(RepoIngestError):
    """`git` failed (missing binary, auth failure, timeout, bad branch...)."""


class SubpathError(RepoIngestError):
    """The requested sub-directory does not exist or is not a directory."""
