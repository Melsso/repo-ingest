from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from repo_ingest.defs.config import DEFAULT_MAX_FILE_SIZE


@dataclass(frozen=True)
class IngestOptions:
    branch: str | None = None
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
    use_default_ignores: bool = True
    use_gitignore: bool = True
    token: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class IngestResult:
    summary: str
    tree: str
    content: str
    files_analyzed: int
    estimated_tokens: int

    @property
    def text(self) -> str:
        return f"{self.summary}\n{self.tree}\n\n{self.content}"


@dataclass
class Node:
    name: str
    path: str
    is_dir: bool
    size: int = 0
    content: str | None = None
    file_count: int = 0
    children: list[Node] = field(default_factory=list)

    def iter_files(self) -> Iterator[Node]:
        for child in self.children:
            if child.is_dir:
                yield from child.iter_files()
            else:
                yield child


@dataclass(frozen=True)
class Source:
    repo: str
    user: str = ""
    url: str | None = None
    local_path: Path | None = None
    branch: str | None = None
    subpath: str = ""
    commit: str | None = None

    @property
    def is_remote(self) -> bool:
        return self.url is not None
