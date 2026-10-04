from importlib.metadata import PackageNotFoundError, version

from repo_ingest.defs import (
    DEFAULT_ALLOWED_HOSTS,
    DEFAULT_MAX_FILE_SIZE,
    IngestOptions,
    IngestResult,
    InvalidSourceError,
    RepoIngestError,
)
from repo_ingest.helpers import parse_source
from repo_ingest.ingest import ingest

try:
    __version__ = version("repo-ingest")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "DEFAULT_ALLOWED_HOSTS",
    "DEFAULT_MAX_FILE_SIZE",
    "IngestOptions",
    "IngestResult",
    "InvalidSourceError",
    "RepoIngestError",
    "ingest",
    "parse_source",
]
