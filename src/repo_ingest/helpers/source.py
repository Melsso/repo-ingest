from __future__ import annotations

from collections.abc import Collection
from pathlib import Path

from repo_ingest.defs import _SHORTHAND_RE, _URL_RE, InvalidSourceError, Source


def parse_source(
    raw: str,
    branch: str | None = None,
    *,
    allow_local: bool = True,
    allowed_hosts: Collection[str] | None = None,
) -> Source:
    raw = raw.strip()
    if allow_local:
        path = Path(raw).expanduser()
        if path.exists():
            resolved = path.resolve()
            return Source(repo=resolved.name, local_path=resolved)

    host = "github.com"
    rest: str | None = None
    if m := _URL_RE.match(raw):
        host, user, repo, rest = m["host"].lower(), m["user"], m["repo"], m["rest"]
    elif m := _SHORTHAND_RE.match(raw):
        user, repo = m["user"], m["repo"]
    else:
        raise InvalidSourceError(f"Not a local path or repository URL: {raw!r}")

    if allowed_hosts is not None and host not in allowed_hosts:
        raise InvalidSourceError(f"Host not allowed: {host}")

    subpath = ""
    if rest:
        if branch and (rest == branch or rest.startswith(branch + "/")):
            subpath = rest[len(branch) :].lstrip("/")
        else:
            first, _, subpath = rest.partition("/")
            branch = branch or first

    if ".." in Path(subpath).parts or subpath.startswith("-"):
        raise InvalidSourceError(f"Invalid subpath: {subpath!r}")

    return Source(
        repo=repo,
        user=user,
        url=f"https://{host}/{user}/{repo}.git",
        branch=branch,
        subpath=subpath,
    )
