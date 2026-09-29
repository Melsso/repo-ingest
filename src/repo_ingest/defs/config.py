from __future__ import annotations

import re

SEPARATOR = "=" * 48

DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_TOTAL_SIZE = 500 * 1024 * 1024
MAX_FILES = 10_000
MAX_DEPTH = 20
CLONE_TIMEOUT_SECONDS = 300
TOKEN_ENCODING = "o200k_base"
EMPTY_FILE_PLACEHOLDER = "[Empty file]"
NON_TEXT_PLACEHOLDER = "[Non-text file]"

DEFAULT_IGNORE_PATTERNS: tuple[str, ...] = (
    ".git",
    ".gitignore",
    ".gitattributes",
    ".svn",
    ".hg",
    ".idea",
    ".vscode",
    ".DS_Store",
    "Thumbs.db",
    "node_modules",
    "bower_components",
    "vendor",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "target",
    ".next",
    ".nuxt",
    "*.egg-info",
    "coverage",
    "package-lock.json",
    "pnpm-lock.yaml",
    "*.lock",
    "bun.lockb",
    "go.sum",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.bmp",
    "*.ico",
    "*.svg",
    "*.webp",
    "*.tiff",
    "*.mp3",
    "*.mp4",
    "*.mov",
    "*.avi",
    "*.wav",
    "*.flac",
    "*.ogg",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.bz2",
    "*.7z",
    "*.rar",
    "*.jar",
    "*.war",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.bin",
    "*.o",
    "*.a",
    "*.class",
    "*.wasm",
    "*.pdf",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.eot",
    "*.otf",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.min.js",
    "*.min.css",
    "*.map",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
)

DEFAULT_ALLOWED_HOSTS: frozenset[str] = frozenset(
    {"github.com", "gitlab.com", "bitbucket.org"}
)

_URL_RE = re.compile(
    r"^(?:https?://)?(?P<host>[^/\s]+\.[^/\s]+)/(?P<user>[^/\s]+)/"
    r"(?P<repo>[^/\s#?]+?)(?:\.git)?"
    r"(?:/(?:tree|blob)/(?P<rest>[^\s?#]+?))?/?$"
)

_SHORTHAND_RE = re.compile(r"^(?P<user>[\w.-]+)/(?P<repo>[\w.-]+)$")
