from __future__ import annotations

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import PlainTextResponse
except ImportError as e:
    raise ImportError("Install the API extra: pip install 'repo-ingest'") from e

from repo_ingest import (
    DEFAULT_ALLOWED_HOSTS,
    IngestOptions,
    IngestResult,
    RepoIngestError,
    __version__,
    ingest,
)
from repo_ingest.api_schemas import IngestRequest, IngestResponse


def _run(req: IngestRequest) -> IngestResult:
    options = IngestOptions(
        branch=req.branch,
        include=tuple(req.include),
        exclude=tuple(req.exclude),
        max_file_size=req.max_file_size,
        token=req.token,
    )
    try:
        return ingest(
            req.source, options, allow_local=False, allowed_hosts=DEFAULT_ALLOWED_HOSTS
        )
    except RepoIngestError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def create_app() -> FastAPI:
    app = FastAPI(title="repo_ingest", version=__version__)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/ingest", response_model=IngestResponse)
    def ingest_json(req: IngestRequest) -> IngestResponse:
        r = _run(req)
        return IngestResponse(
            summary=r.summary,
            tree=r.tree,
            content=r.content,
            files_analyzed=r.files_analyzed,
            estimated_tokens=r.estimated_tokens,
        )

    @app.post("/ingest.txt", response_class=PlainTextResponse)
    def ingest_text(req: IngestRequest) -> str:
        return _run(req).text

    return app


app = create_app()
