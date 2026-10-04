from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from urllib.parse import urlsplit

from repo_ingest.defs import CLONE_TIMEOUT_SECONDS, CloneError, Source

_TOKEN_USERNAMES = {
    "github.com": "x-access-token",
    "gitlab.com": "oauth2",
    "bitbucket.org": "x-token-auth",
}


def _auth_env(url: str, token: str) -> tuple[dict[str, str], str]:
    parts = urlsplit(url)
    user = _TOKEN_USERNAMES.get(parts.hostname or "", "x-access-token")
    basic = base64.b64encode(f"{user}:{token}".encode()).decode()
    env = {
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": f"http.{parts.scheme}://{parts.hostname}/.extraHeader",
        "GIT_CONFIG_VALUE_0": f"Authorization: Basic {basic}",
    }
    return env, basic


def _git(
    args: Sequence[str],
    cwd: Path | None = None,
    extra_env: Mapping[str, str] | None = None,
    secrets: Sequence[str] = (),
) -> str:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", **(extra_env or {})}
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
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
    auth: dict[str, str] = {}
    secrets: list[str] = []
    if token:
        auth, basic = _auth_env(source.url, token)
        secrets = [token, basic]

    with tempfile.TemporaryDirectory(prefix="repo_ingest_") as tmp:
        dest = Path(tmp) / "repo"
        args = ["clone", "--depth=1", "--single-branch"]
        if source.branch:
            args += ["--branch", source.branch]
        if source.subpath:
            args += ["--filter=blob:none", "--sparse"]
        _git([*args, "--", source.url, str(dest)], extra_env=auth, secrets=secrets)
        if source.subpath:
            _git(
                ["sparse-checkout", "set", source.subpath],
                cwd=dest,
                extra_env=auth,
                secrets=secrets,
            )
        commit = _git(["rev-parse", "HEAD"], cwd=dest)
        branch = source.branch
        if not branch:
            try:
                branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=dest)
            except CloneError:
                branch = None
        yield replace(source, local_path=dest, commit=commit, branch=branch)
