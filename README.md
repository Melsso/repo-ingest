# repo_ingest

Turn a git repository into a single LLM-friendly text digest (summary, directory tree,
file contents) so you can hand a whole codebase to a model in one paste, without wasting
tokens on lockfiles, binaries and build output.

## Install (Poetry)

```bash
poetry install                      # core + dev tools
poetry install --extras api         # + FastAPI service
poetry install --extras clipboard   # + --clip support
```

Requires Python 3.10+ and `git` on your PATH (for remote repos).

## CLI

```bash
poetry run repo_ingest https://github.com/owner/repo -o digest.txt
poetry run repo_ingest owner/repo -i "*.py" -e "tests/*"
poetry run repo_ingest https://github.com/owner/repo/tree/dev/src
poetry run repo_ingest ./local/project --clip
poetry run repo_ingest owner/private-repo --token $GITHUB_TOKEN
```

Options: `-b/--branch`, `-i/--include GLOB`, `-e/--exclude GLOB`, `--max-size BYTES`,
`--no-default-ignores`, `--no-gitignore`, `--token`, `--clip`, `-o/--output`.

## Library

```python
from repo_ingest import ingest, IngestOptions

result = ingest("owner/repo", IngestOptions(include=("*.py",), exclude=("tests",)))
print(result.estimated_tokens)
open("digest.txt", "w").write(result.text)
```

## HTTP service

```bash
poetry run uvicorn repo_ingest.api:app --port 8000
curl -X POST localhost:8000/ingest.txt -H 'content-type: application/json' \
     -d '{"source": "https://github.com/owner/repo"}'
```

The API refuses local paths and only clones from github.com, gitlab.com and bitbucket.org
(see `DEFAULT_ALLOWED_HOSTS` in `config.py`). If you expose it publicly, also add auth,
rate limiting, and a concurrency cap.

## Layout

```
src/repo_ingest/
  
  defs/
    __init__.py
    config.py      limits, separators, default ignore patterns
    models.py      IngestOptions, IngestResult, Node
    errors.py      
    schemas.py.    api contracts

  helpers/
    __init__.py
    git.py         shallow + sparse clone in a temp dir (token redaction, no prompts)
    render.py      tree, contents and summary text, tiktoken estimate with chars/4 fallback
    source.py      parse URL / owner/repo / local path -> Source
    walker.py      traversal with size/count limits -> Node tree, include / exclude / .gitignore matching, text detection and decoding
  
  __init__.py
  __main__.py
  cli.py       argparse CLI
  api.py       optional FastAPI app
  ingest.py    orchestration (the public ingest())

tests/
```

## Development

```bash
poetry run pytest
poetry run ruff check . && poetry run mypy .
```
