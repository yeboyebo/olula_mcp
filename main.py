import os
import contextlib
import argparse

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import ASGIApp, Receive, Scope, Send
import uvicorn

from server import mcp
from client import set_request_headers


class AuthForwardMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            headers_dict = dict(scope.get("headers", []))
            auth: dict = {}
            if b"authorization" in headers_dict:
                auth["authorization"] = headers_dict[b"authorization"].decode("latin-1")
            if b"x-api-key" in headers_dict:
                auth["x-api-key"] = headers_dict[b"x-api-key"].decode("latin-1")
            set_request_headers(auth if auth else None)
        try:
            await self.app(scope, receive, send)
        finally:
            if scope["type"] in ("http", "websocket"):
                set_request_headers(None)


def _build_http_app() -> ASGIApp:
    sse_app = mcp.sse_app()
    streamable_app = mcp.streamable_http_app()

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp._session_manager.run():
            yield

    routes = [
        Mount("/", app=sse_app),
        Mount("/", app=streamable_app),
    ]

    app = Starlette(
        debug=mcp.settings.debug,
        routes=routes,
        lifespan=lifespan,
    )
    return AuthForwardMiddleware(app)


def main():
    parser = argparse.ArgumentParser(description="Olula MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=os.environ.get("MCP_TRANSPORT", "http"),
        help="Transport: 'stdio' for stdin, 'http' for SSE + Streamable HTTP (default: http)",
    )
    parser.add_argument("--host", default=None, help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Port (default: 8000)")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        host = args.host or mcp.settings.host
        port = args.port or mcp.settings.port
        app = _build_http_app()
        uvicorn.run(app, host=host, port=port, log_level=mcp.settings.log_level.lower())


if __name__ == "__main__":
    main()