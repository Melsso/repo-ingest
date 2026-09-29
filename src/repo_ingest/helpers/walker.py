from __future__ import annotations

import fnmatch
from collections.abc import Iterable
from pathlib import Path
from types import ModuleType

from repo_ingest.defs import (
    EMPTY_FILE_PLACEHOLDER,
    MAX_DEPTH,
    MAX_FILES,
    MAX_TOTAL_SIZE,
    NON_TEXT_PLACEHOLDER,
    Node,
)

pathspec: ModuleType | None

try:
    import pathspec
except ImportError:
    pathspec = None


def _sort_key(node: Node) -> tuple[bool, bool, str]:
    return (not node.name.lower().startswith("readme"), node.is_dir, node.name.lower())


def matches_any(rel: str, name: str, patterns: Iterable[str]) -> bool:
    for raw in patterns:
        pat = raw.strip().rstrip("/")
        if not pat:
            continue
        if (
            fnmatch.fnmatch(name, pat)
            or fnmatch.fnmatch(rel, pat)
            or fnmatch.fnmatch(rel, pat + "/*")
        ):
            return True
    return False


def is_text_file(path: Path, sniff_bytes: int = 4096) -> bool:
    try:
        with path.open("rb") as fh:
            chunk = fh.read(sniff_bytes)
    except OSError:
        return False
    return b"\x00" not in chunk


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, OSError):
            continue
    return "Error reading file"


def read_gitignore(root: Path) -> list[str]:
    gi = root / ".gitignore"
    if not gi.is_file():
        return []
    return [
        line.strip()
        for line in gi.read_text(errors="ignore").splitlines()
        if line.strip() and not line.startswith("#")
    ]


class PathFilter:
    def __init__(
        self,
        include: Iterable[str] = (),
        exclude: Iterable[str] = (),
        gitignore_lines: Iterable[str] = (),
    ) -> None:
        self._include = [p for p in include if p.strip()]
        self._exclude = list(exclude)
        self._spec = None
        lines = list(gitignore_lines)
        if lines:
            if pathspec is not None:
                self._spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
            else:
                self._exclude += [ln for ln in lines if not ln.startswith("!")]

    def is_excluded(self, rel: str, name: str, is_dir: bool) -> bool:
        if matches_any(rel, name, self._exclude):
            return True
        return bool(self._spec and self._spec.match_file(rel + "/" if is_dir else rel))

    def is_included(self, rel: str, name: str) -> bool:
        return not self._include or matches_any(rel, name, self._include)


class Walker:
    def __init__(self, root: Path, path_filter: PathFilter, max_file_size: int) -> None:
        self.root = root
        self.filter = path_filter
        self.max_file_size = max_file_size
        self.total_files = 0
        self.total_size = 0

    def scan(self) -> Node:
        return self._walk(self.root, depth=0)

    def _walk(self, directory: Path, depth: int) -> Node:
        rel_dir = (
            ""
            if directory == self.root
            else directory.relative_to(self.root).as_posix()
        )
        node = Node(name=directory.name, path=rel_dir, is_dir=True)
        if depth > MAX_DEPTH:
            return node
        try:
            entries = list(directory.iterdir())
        except OSError:
            return node

        for entry in entries:
            if entry.is_symlink():
                continue
            rel = entry.relative_to(self.root).as_posix()
            is_dir = entry.is_dir()
            if self.filter.is_excluded(rel, entry.name, is_dir):
                continue
            if is_dir:
                child = self._walk(entry, depth + 1)
                if child.file_count:
                    node.children.append(child)
                    node.file_count += child.file_count
                    node.size += child.size
            elif entry.is_file():
                file_node = self._read_file(entry, rel)
                if file_node is not None:
                    node.children.append(file_node)
                    node.file_count += 1
                    node.size += file_node.size

        node.children.sort(key=_sort_key)
        return node

    def _read_file(self, path: Path, rel: str) -> Node | None:
        if not self.filter.is_included(rel, path.name):
            return None
        size = path.stat().st_size
        if size > self.max_file_size:
            return None
        if self.total_files >= MAX_FILES or self.total_size + size > MAX_TOTAL_SIZE:
            return None

        if size == 0:
            content = EMPTY_FILE_PLACEHOLDER
        elif is_text_file(path):
            content = read_text(path)
        else:
            content = NON_TEXT_PLACEHOLDER

        self.total_files += 1
        self.total_size += size
        return Node(
            name=path.name,
            path=rel,
            is_dir=False,
            size=size,
            content=content,
            file_count=1,
        )
