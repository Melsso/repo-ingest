# repo-ingest

Turn a git repository into a single LLM-friendly text digest: a summary, a directory
tree and the contents of every relevant file, plus a token estimate. Hand a whole
codebase to a model in one paste, without wasting tokens on lockfiles, binaries and
build output.

## Installation

Requires Python 3.11+ and `git` on your `PATH` (for remote repositories).

```bash
pip install "repo-ingest[api] @ git+https://github.com/Melsso/repo-ingest.git@v0.1.0"

# with optional extras
pipx install "repo-ingest[api,clipboard] @ git+https://github.com/Melsso/repo-ingest.git@v0.1.0"
```

| Extra       | Adds                          |
|-------------|-------------------------------|
| `api`       | the FastAPI service + uvicorn |
| `clipboard` | `--clip` support (pyperclip)  |

## CLI

```bash
repo_ingest https://github.com/owner/repo -o digest.txt
repo_ingest owner/repo -i "*.py" -e "tests/*"
repo_ingest https://github.com/owner/repo/tree/dev/src
repo_ingest ./local/project --clip
REPO_INGEST_TOKEN=... repo_ingest owner/private-repo
```

| Option                  | Meaning                                                        |
|-------------------------|----------------------------------------------------------------|
| `-o, --output FILE`     | write the digest to a file (default: stdout)                   |
| `-b, --branch NAME`     | branch or tag to clone                                         |
| `-i, --include GLOB`    | only include matching paths (repeatable)                       |
| `-e, --exclude GLOB`    | exclude matching paths (repeatable)                            |
| `--max-size BYTES`      | skip files larger than this (default 10 MB)                    |
| `--no-default-ignores`  | don't apply the built-in ignore list                           |
| `--no-gitignore`        | don't apply the repository's root `.gitignore`                 |
| `--token TOKEN`         | access token for private https repos (prefer `REPO_INGEST_TOKEN`) |
| `--clip`                | copy the digest to the clipboard                               |

Exit codes: `0` success, `1` expected error (bad source, clone failure), `2` missing
optional dependency.

### What gets skipped

By default: VCS metadata, dependency and build directories (`node_modules`, `dist`,
`.venv`, ...), lockfiles, images/audio/video/archives/binaries, minified files,
`.env*` files and private keys (see `DEFAULT_IGNORE_PATTERNS` in `defs/config.py`).
Symlinks are never followed. Limits: 10,000 files, 500 MB total, 20 directory levels.
Binary files that pass the filters appear as `[Non-text file]`.

## Library

```python
from repo_ingest import ingest, IngestOptions

result = ingest("owner/repo", IngestOptions(include=("*.py",), exclude=("tests",)))
print(result.estimated_tokens)
with open("digest.txt", "w", encoding="utf-8") as f:
    f.write(result.text)
```

## HTTP service

```bash
pip install "repo-ingest[api]"
uvicorn repo_ingest.api:app --port 8000
curl -X POST localhost:8000/ingest.txt -H 'content-type: application/json' \
     -d '{"source": "https://github.com/owner/repo"}'
```

The API refuses local paths and only clones from github.com, gitlab.com and
bitbucket.org (`DEFAULT_ALLOWED_HOSTS`). It has **no authentication, rate limiting or
concurrency cap**: put it behind a gateway before exposing it publicly.

## Security notes

- Access tokens are passed to git through an environment-injected auth header: never in
  argv, the clone URL or `.git/config`. They are redacted from error messages and
  hidden from `repr()`.
- Local paths are rejected by the API; subpaths containing `..` are rejected everywhere.
- Prefer `REPO_INGEST_TOKEN` over `--token`: command-line arguments are visible to
  other users via `ps` and end up in shell history.

## Limitations

- Only the root `.gitignore` is honored; nested ones are ignored.
- `tree/<ref>/<path>` URLs are ambiguous when the branch name contains `/`; pass
  `--branch` explicitly.
- Token counts use the `o200k_base` encoding (chars/4 estimate if it can't be loaded,
  e.g. offline).

## Project layout

```
src/repo_ingest/
  cli.py          argparse CLI
  api.py          optional FastAPI app
  api_schemas.py  request/response models for the API
  ingest.py       orchestration: the public ingest()
  defs/
    config.py     limits, separators, default ignore patterns
    models.py     IngestOptions, IngestResult, Node, Source
    errors.py     RepoIngestError and subclasses
  helpers/
    git.py        shallow + sparse clone in a temp dir (token redaction, no prompts)
    render.py     tree, contents and summary text; token estimate
    source.py     parse URL / owner/repo / local path into a Source
    walker.py     traversal with limits; include/exclude/.gitignore matching
tests/
```

## Development

```bash
poetry install --all-extras
poetry run pytest
poetry run ruff check . && poetry run mypy .
```

## License

MIT. See [LICENSE](LICENSE).