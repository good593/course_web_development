from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(code: str, message: str, details=None):
    body = {"success": False, "error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            field_path = ".".join(str(loc) for loc in err["loc"][1:])
            errors.append({
                "field": field_path,
                "message": err["msg"],
                "type": err["type"],
            })

        return JSONResponse(
            status_code=422,
            content=error_response("VALIDATION_ERROR", "입력값이 올바르지 않습니다.", errors),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            return JSONResponse(
                status_code=exc.status_code,
                content={"success": False, "error": exc.detail},
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response("HTTP_ERROR", str(exc.detail)),
        )
