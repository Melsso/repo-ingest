from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from repo_ingest import DEFAULT_MAX_FILE_SIZE, IngestOptions, RepoIngestError, ingest


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="repo_ingest", description="Turn a repo into one LLM-friendly text digest."
    )
    p.add_argument("source", help="GitHub/GitLab URL, owner/repo, or local path")
    p.add_argument("-o", "--output", help="write digest to this file (default: stdout)")
    p.add_argument("-b", "--branch")
    p.add_argument("-i", "--include", action="append", default=[], metavar="GLOB")
    p.add_argument("-e", "--exclude", action="append", default=[], metavar="GLOB")
    p.add_argument(
        "--max-size", type=int, default=DEFAULT_MAX_FILE_SIZE, help="bytes per file"
    )
    p.add_argument("--no-default-ignores", action="store_true")
    p.add_argument("--no-gitignore", action="store_true")
    p.add_argument(
        "--token", help="access token (prefer the REPO_INGEST_TOKEN env var)"
    )
    p.add_argument("--clip", action="store_true", help="copy digest to clipboard")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    options = IngestOptions(
        branch=args.branch,
        include=tuple(args.include),
        exclude=tuple(args.exclude),
        max_file_size=args.max_size,
        use_default_ignores=not args.no_default_ignores,
        use_gitignore=not args.no_gitignore,
        token=args.token or os.environ.get("REPO_INGEST_TOKEN"),
    )
    try:
        result = ingest(args.source, options)
    except RepoIngestError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.clip:
        try:
            import pyperclip
        except ImportError:
            print(
                "error: --clip needs `pip install repo-ingest[clipboard]`",
                file=sys.stderr,
            )
            return 2
        pyperclip.copy(result.text)
    if args.output:
        Path(args.output).write_text(result.text, encoding="utf-8")
    if args.output or args.clip:
        print(result.summary, file=sys.stderr)
    else:
        sys.stdout.write(result.text)
    return 0
