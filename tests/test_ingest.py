from repo_ingest import IngestOptions, ingest


def test_default_behaviour(demo_repo):
    r = ingest(str(demo_repo))
    assert "FILE: README.md" in r.content
    assert "FILE: src/main.py" in r.content
    assert "node_modules" not in r.tree
    assert ".env" not in r.tree
    assert "skipme.txt" not in r.tree
    assert "[Non-text file]" in r.content
    assert ".gitignore" not in r.tree
    assert r.files_analyzed == 4


def test_readme_first_then_files_then_dirs(demo_repo):
    lines = ingest(str(demo_repo)).tree.splitlines()
    names = [ln.split("── ")[-1] for ln in lines[2:]]
    assert names[0] == "README.md"
    assert names.index("blob.dat") < names.index("src/")


def test_include_exclude(demo_repo):
    r = ingest(str(demo_repo), IngestOptions(include=("*.py",), exclude=("tests",)))
    assert r.files_analyzed == 1
    assert "test_a.py" not in r.tree


def test_max_file_size(demo_repo):
    r = ingest(str(demo_repo), IngestOptions(max_file_size=5))
    assert "main.py" not in r.tree


def test_summary_has_token_estimate(demo_repo):
    r = ingest(str(demo_repo))
    assert "Estimated tokens:" in r.summary and r.estimated_tokens > 0
    assert r.text.startswith("Repository:")
