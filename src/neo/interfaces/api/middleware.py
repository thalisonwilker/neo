"""Middleware de observabilidade HTTP sem exposicao de dados sensiveis."""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("neo.api")


class ObservabilidadeMiddleware(BaseHTTPMiddleware):
    """Registra metodo, rota, status, duracao e request_id, alem da contagem de 401/403."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        inicio = time.perf_counter()
        response = await call_next(request)
        duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        metricas: dict[str, int] = getattr(
            request.app.state,
            "metricas_recusas",
            {"401": 0, "403": 0},
        )
        if response.status_code in (401, 403):
            chave = str(response.status_code)
            metricas[chave] = metricas.get(chave, 0) + 1
            logger.warning(
                "metodo=%s rota=%s status=%d duracao_ms=%.2f request_id=%s recusas_%s=%d",
                request.method,
                request.url.path,
                response.status_code,
                duracao_ms,
                request_id,
                chave,
                metricas[chave],
            )
        else:
            logger.info(
                "metodo=%s rota=%s status=%d duracao_ms=%.2f request_id=%s",
                request.method,
                request.url.path,
                response.status_code,
                duracao_ms,
                request_id,
            )

        return response
