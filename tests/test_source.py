import pytest

from repo_ingest import InvalidSourceError, parse_source


def test_full_url():
    s = parse_source("https://github.com/o/r", allow_local=False)
    assert (s.user, s.repo, s.url) == ("o", "r", "https://github.com/o/r.git")


def test_shorthand():
    assert parse_source("o/r", allow_local=False).url == "https://github.com/o/r.git"


def test_tree_url_branch_and_subpath():
    s = parse_source("https://github.com/o/r/tree/dev/src/pkg", allow_local=False)
    assert (s.branch, s.subpath) == ("dev", "src/pkg")


def test_explicit_branch_with_slash():
    s = parse_source(
        "https://github.com/o/r/tree/feature/x/src", "feature/x", allow_local=False
    )
    assert (s.branch, s.subpath) == ("feature/x", "src")


def test_git_suffix_stripped():
    assert parse_source("https://github.com/o/r.git", allow_local=False).repo == "r"


def test_host_allowlist():
    with pytest.raises(InvalidSourceError):
        parse_source(
            "https://evil.example/o/r", allow_local=False, allowed_hosts={"github.com"}
        )


def test_local_refused_when_disallowed(tmp_path):
    with pytest.raises(InvalidSourceError):
        parse_source(str(tmp_path), allow_local=False)


def test_subpath_traversal_rejected():
    with pytest.raises(InvalidSourceError):
        parse_source("https://github.com/o/r/tree/main/../../etc", allow_local=False)


def test_garbage_rejected():
    with pytest.raises(InvalidSourceError):
        parse_source("not a repo", allow_local=False)
