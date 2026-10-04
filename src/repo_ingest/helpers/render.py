from __future__ import annotations

from functools import lru_cache
from typing import Any

from repo_ingest.defs import SEPARATOR, TOKEN_ENCODING, Node, Source


@lru_cache(maxsize=1)
def _encoder() -> Any | None:
    try:
        import tiktoken

        return tiktoken.get_encoding(TOKEN_ENCODING)
    except Exception:  # noqa: BLE001 - network errors, missing cache, bad install
        return None


def count_tokens(text: str) -> int:
    enc = _encoder()
    if enc is None:
        return len(text) // 4
    return len(enc.encode(text, disallowed_special=()))


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def render_tree(root: Node) -> str:
    lines = ["Directory structure:", f"└── {root.name}/"]
    _render_children(root, "    ", lines)
    return "\n".join(lines)


def _render_children(node: Node, prefix: str, lines: list[str]) -> None:
    for i, child in enumerate(node.children):
        last = i == len(node.children) - 1
        marker = "└── " if last else "├── "
        lines.append(f"{prefix}{marker}{child.name}{'/' if child.is_dir else ''}")
        if child.is_dir:
            _render_children(child, prefix + ("    " if last else "│   "), lines)


def render_contents(root: Node) -> str:
    blocks = (
        f"{SEPARATOR}\nFILE: {f.path}\n{SEPARATOR}\n{f.content}\n"
        for f in root.iter_files()
    )
    return "\n".join(blocks)


def render_summary(source: Source, files_analyzed: int, estimated_tokens: int) -> str:
    name = f"{source.user}/{source.repo}" if source.user else source.repo
    lines = [f"Repository: {name}"]
    if source.is_remote and source.branch:
        lines.append(f"Branch: {source.branch}")
    if source.commit:
        lines.append(f"Commit: {source.commit}")
    if source.subpath:
        lines.append(f"Subpath: /{source.subpath}")
    lines.append(f"Files analyzed: {files_analyzed}")
    return "\n".join(lines) + f"\n\nEstimated tokens: {format_tokens(estimated_tokens)}"
