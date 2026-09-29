from repo_ingest.cli import main


def test_stdout(demo_repo, capsys):
    assert main([str(demo_repo)]) == 0
    assert "FILE: src/main.py" in capsys.readouterr().out


def test_output_file(demo_repo, tmp_path, capsys):
    out = tmp_path / "out.txt"
    assert main([str(demo_repo), "-o", str(out)]) == 0
    assert "Directory structure:" in out.read_text()
    assert "Files analyzed" in capsys.readouterr().err


def test_bad_source(capsys):
    assert main(["definitely not valid"]) == 1
    assert "error:" in capsys.readouterr().err
