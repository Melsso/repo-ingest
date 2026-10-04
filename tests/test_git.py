import shutil
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
    key = calls[0][1]["GIT_CONFIG_KEY_0"]
    assert key.endswith(".extraHeader") and "github.com" in key


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


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_cloned_real_git_with_subpath(tmp_path):
    origin = tmp_path / "origin"
    (origin / "pkg").mkdir(parents=True)
    (origin / "other").mkdir()
    (origin / "pkg" / "a.py").write_text("print(1)\n")
    (origin / "other" / "b.py").write_text("print(2)\n")

    def git(*args):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
            cwd=origin,
            check=True,
            capture_output=True,
        )

    git("init", "-b", "main")
    git("add", ".")
    git("commit", "-m", "init")

    src = Source(repo="origin", url=origin.as_uri(), subpath="pkg")
    with git_mod.cloned(src) as checked_out:
        assert checked_out.local_path is not None
        assert (checked_out.local_path / "pkg" / "a.py").exists()
        assert not (checked_out.local_path / "other").exists()
        assert checked_out.commit and checked_out.branch == "main"
