from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.config import settings
from app.integrations import configure_workflow_integrations
from app.security import RequestGuardMiddleware


def create_app() -> FastAPI:
    configure_workflow_integrations()
    application = FastAPI(
        title="Byapari API",
        version="1.0.0",
        description="Durable orchestration API for accountable business workflows.",
    )
    application.add_middleware(GZipMiddleware, minimum_size=1_000)
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(settings.trusted_hosts),
    )
    application.add_middleware(RequestGuardMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix="/api/v1")

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    @application.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "The request did not match the API contract.",
                    "details": [
                        {"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()
                    ],
                },
            },
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict):
            code = str(exc.detail.get("code", "REQUEST_FAILED"))
            message = str(exc.detail.get("message", "The request could not be completed."))
        else:
            code = "REQUEST_FAILED"
            message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "success": False,
                "error": {"code": code, "message": message},
            },
        )

    return application


app = create_app()
