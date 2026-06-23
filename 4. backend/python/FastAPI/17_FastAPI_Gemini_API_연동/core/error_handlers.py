from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.genai import errors


async def gemini_error_handler(request: Request, exc: errors.APIError):
    status_map = {429: 429, 403: 401, 400: 400}
    status_code = status_map.get(exc.code, 502)
    message = exc.message or str(exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": f"Gemini API 오류: {message}",
            "code": exc.code,
            "status": exc.status,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(errors.APIError, gemini_error_handler)
