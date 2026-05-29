import json
from contextvars import ContextVar

import requests

from config import API_HOST, API_KEY

_request_headers: ContextVar[dict | None] = ContextVar("_request_headers", default=None)


def set_request_headers(headers: dict | None) -> None:
    _request_headers.set(headers)


def _headers() -> dict:
    result: dict = {}
    auth_header: str | None = None

    # 1. Extraer directamente del contexto de request MCP
    try:
        from server import mcp
        ctx = mcp.get_context()
        req = ctx.request_context.request
        if req is not None:
            auth_header = req.headers.get("authorization")
    except Exception:
        pass

    # 2. Fallback: ContextVar del middleware
    if not auth_header:
        incoming = _request_headers.get()
        if incoming:
            auth_header = incoming.get("authorization")

    # 3. Transformar Bearer a X-Api-Key para el WebService
    token: str | None = None
    if auth_header:
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
        else:
            token = auth_header
    elif API_KEY:
        token = API_KEY

    if token:
        result["Authorization"] = f"X-Api-Key {token}"

    return result


def api_get(path: str, params: dict | None = None) -> dict | list:
    response = requests.get(f"{API_HOST}{path}", params=params, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


def api_get_one(path: str, params: dict | None = None) -> dict:
    result = api_get(path, params)
    if not isinstance(result, dict):
        raise ValueError(f"Expected dict from {path}, got {type(result).__name__}")
    return result


def api_get_many(path: str, params: dict | None = None) -> list[dict]:
    result = api_get(path, params)
    if not isinstance(result, list):
        raise ValueError(f"Expected list from {path}, got {type(result).__name__}")
    return result


def api_post(path: str, body: dict | None = None) -> dict:
    response = requests.post(f"{API_HOST}{path}", json=body, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


def api_patch(path: str, body: dict | None = None) -> dict:
    response = requests.patch(f"{API_HOST}{path}", json=body, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


def api_put(path: str, body: dict | None = None) -> dict:
    response = requests.put(f"{API_HOST}{path}", json=body, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


def api_delete(path: str) -> dict | None:
    response = requests.delete(f"{API_HOST}{path}", headers=_headers())
    response.raise_for_status()
    if response.text:
        data = response.json()
        return data.get("datos", data)
    return None


def build_query(filtro: list | None = None, orden: list | None = None, pagina: int = 1, limite: int = 100) -> str:
    q: dict = {"paginacion": {"pagina": pagina, "limite": limite}}
    if filtro:
        q["filtro"] = filtro
    if orden:
        q["orden"] = orden
    return json.dumps(q, ensure_ascii=False, separators=(",", ":"))