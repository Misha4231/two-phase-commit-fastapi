import uuid

from fastapi import Request

from common.core.context import request_id_ctx_var


async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    request_id_ctx_var.set(request_id)
    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    return response
