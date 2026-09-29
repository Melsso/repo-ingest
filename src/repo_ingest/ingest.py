from __future__ import annotations

from collections.abc import Collection

from repo_ingest.defs import (
    DEFAULT_IGNORE_PATTERNS,
    IngestOptions,
    IngestResult,
    Source,
    SubpathError,
)
from repo_ingest.helpers import (
    PathFilter,
    Walker,
    cloned,
    count_tokens,
    parse_source,
    read_gitignore,
    render_contents,
    render_summary,
    render_tree,
)


def ingest(
    source: str,
    options: IngestOptions | None = None,
    *,
    allow_local: bool = True,
    allowed_hosts: Collection[str] | None = None,
) -> IngestResult:
    options = options or IngestOptions()
    parsed = parse_source(
        source, options.branch, allow_local=allow_local, allowed_hosts=allowed_hosts
    )
    if parsed.is_remote:
        with cloned(parsed, options.token) as checked_out:
            return _build(checked_out, options)
    return _build(parsed, options)


def _build(source: Source, options: IngestOptions) -> IngestResult:
    assert source.local_path is not None
    repo_root = source.local_path.resolve()
    root = (repo_root / source.subpath).resolve()
    if not root.is_relative_to(repo_root) or not root.is_dir():
        raise SubpathError(f"Subpath not found or not a directory: /{source.subpath}")

    exclude = (
        DEFAULT_IGNORE_PATTERNS if options.use_default_ignores else ()
    ) + options.exclude
    gitignore = read_gitignore(root) if options.use_gitignore else []
    walker = Walker(
        root, PathFilter(options.include, exclude, gitignore), options.max_file_size
    )

    tree_root = walker.scan()
    tree_root.name = (
        f"{source.repo}/{source.subpath}".rstrip("/") if source.subpath else source.repo
    )

    tree = render_tree(tree_root)
    content = render_contents(tree_root)
    tokens = count_tokens(tree + content)
    summary = render_summary(source, walker.total_files, tokens)
    return IngestResult(summary, tree, content, walker.total_files, tokens)
