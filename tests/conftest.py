import pytest


@pytest.fixture
def demo_repo(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "node_modules" / "x").mkdir(parents=True)
    (tmp_path / "README.md").write_text("# Demo\n")
    (tmp_path / "src" / "main.py").write_text("print('hi')\n")
    (tmp_path / "tests" / "test_a.py").write_text("def t(): pass\n")
    (tmp_path / "node_modules" / "x" / "i.js").write_text("x")
    (tmp_path / ".env").write_text("SECRET=1\n")
    (tmp_path / "blob.dat").write_bytes(b"\x00\x01\x02")
    (tmp_path / "skipme.txt").write_text("ignored via .gitignore\n")
    (tmp_path / ".gitignore").write_text("skipme.txt\n")
    return tmp_path
