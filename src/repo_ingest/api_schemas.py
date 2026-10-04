from pydantic import BaseModel, Field

from repo_ingest.defs.config import DEFAULT_MAX_FILE_SIZE


class IngestRequest(BaseModel):
    source: str = Field(
        description="Repository URL or owner/repo (local paths are refused)"
    )
    branch: str | None = None
    include: list[str] = []
    exclude: list[str] = []
    max_file_size: int = Field(DEFAULT_MAX_FILE_SIZE, le=DEFAULT_MAX_FILE_SIZE, gt=0)
    token: str | None = Field(None, repr=False)


class IngestResponse(BaseModel):
    summary: str
    tree: str
    content: str
    files_analyzed: int
    estimated_tokens: int
