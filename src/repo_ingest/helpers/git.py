from __future__ import annotations

import os
import subprocess
import tempfile
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

from repo_ingest.defs import CLONE_TIMEOUT_SECONDS, CloneError, Source


def _git(
    args: Sequence[str], cwd: Path | None = None, secrets: Sequence[str] = ()
) -> str:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=CLONE_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as e:
        raise CloneError("git executable not found on PATH") from e
    except subprocess.TimeoutExpired as e:
        raise CloneError(
            f"git {args[0]} timed out after {CLONE_TIMEOUT_SECONDS}s"
        ) from e
    if proc.returncode != 0:
        err = proc.stderr.strip()
        for secret in secrets:
            err = err.replace(secret, "***")
        raise CloneError(f"git {args[0]} failed: {err}")
    return proc.stdout.strip()


@contextmanager
def cloned(source: Source, token: str | None = None) -> Iterator[Source]:
    assert source.url, "cloned() requires a remote source"
    with tempfile.TemporaryDirectory(prefix="repo_ingest_") as tmp:
        dest = Path(tmp) / "repo"
        url = source.url
        if token:
            url = url.replace("https://", f"https://{token}@", 1)
        args = ["clone", "--depth=1", "--single-branch"]
        if source.branch:
            args += ["--branch", source.branch]
        if source.subpath:
            args += ["--filter=blob:none", "--sparse"]
        secrets = [token] if token else []
        _git([*args, "--", url, str(dest)], secrets=secrets)
        if source.subpath:
            _git(["sparse-checkout", "set", source.subpath], cwd=dest)
        commit = _git(["rev-parse", "HEAD"], cwd=dest)
        branch = source.branch
        if not branch:
            try:
                branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=dest)
            except CloneError:
                branch = None
        yield replace(source, local_path=dest, commit=commit, branch=branch)
