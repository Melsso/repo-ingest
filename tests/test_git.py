import subprocess

import pytest

from repo_ingest import IngestOptions
from repo_ingest.defs import CloneError, Source
from repo_ingest.helpers import git as git_mod
from repo_ingest.helpers import render

SRC = Source(repo="r", user="o", url="https://github.com/o/r.git")
TOKEN = "ghp_supersecret"


def test_failed_clone_raises_clone_error_without_token(monkeypatch):
    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 128, "", f"fatal: auth {TOKEN}")

    monkeypatch.setattr(git_mod.subprocess, "run", run)
    with pytest.raises(CloneError) as exc, git_mod.cloned(SRC, TOKEN):
        pass
    assert TOKEN not in str(exc.value)


def test_token_never_appears_in_argv(monkeypatch):
    calls = []

    def run(cmd, **kw):
        calls.append((cmd, kw["env"]))
        return subprocess.CompletedProcess(cmd, 0, "abc", "")

    monkeypatch.setattr(git_mod.subprocess, "run", run)
    with git_mod.cloned(SRC, TOKEN):
        pass
    assert all(TOKEN not in " ".join(cmd) for cmd, _ in calls)
    assert "http.extraHeader" in calls[0][1]["GIT_CONFIG_KEY_0"]


def test_token_not_in_repr():
    assert TOKEN not in repr(IngestOptions(token=TOKEN))


def test_token_count_falls_back_when_offline(monkeypatch):
    import tiktoken

    def boom(*a, **k):
        raise ConnectionError("offline")

    monkeypatch.setattr(tiktoken, "get_encoding", boom)
    render._encoder.cache_clear()
    assert render.count_tokens("x" * 40) == 10
    render._encoder.cache_clear()
