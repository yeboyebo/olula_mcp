import calendar
import json
from contextvars import ContextVar
from datetime import date, timedelta

import httpx

from config import API_HOST, API_KEY

_request_headers: ContextVar[dict | None] = ContextVar("_request_headers", default=None)

# Timeout explícito por fase: sin esto, una petición al backend que se queda
# colgada (típicamente una consulta pesada de agregación) no falla nunca —
# se queda esperando indefinidamente y el usuario ve "minutos sin respuesta"
# en vez de un error rápido y reintentable.
_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)

# Cliente HTTP compartido: reutiliza conexiones (keep-alive/pooling) en vez
# de pagar un handshake TCP/TLS nuevo en cada llamada — se nota especialmente
# en los flujos que paginan varias veces contra el mismo backend.
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=API_HOST, timeout=_TIMEOUT)
    return _client


async def aclose_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


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

    # 3. Reenviar la cabecera Authorization TAL CUAL al WebService.
    # Cuando quien llama al MCP es nuestro propio backend (p.ej. el asistente IA),
    # el Authorization que llega ya es un Bearer de sesión válido contra ese mismo
    # backend — no hay que transformarlo. Solo cuando no llega ninguna Authorization
    # (llamada sin usuario detrás) se usa la API Key fija configurada, enviada como
    # X-Api-Key.
    if auth_header:
        result["Authorization"] = auth_header
    elif API_KEY:
        result["Authorization"] = f"X-Api-Key {API_KEY}"

    return result


async def api_get(path: str, params: dict | None = None) -> dict | list:
    response = await _get_client().get(path, params=params, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


async def api_get_one(path: str, params: dict | None = None) -> dict:
    result = await api_get(path, params)
    if not isinstance(result, dict):
        raise ValueError(f"Expected dict from {path}, got {type(result).__name__}")
    return result


async def api_get_many(path: str, params: dict | None = None) -> list[dict]:
    result = await api_get(path, params)
    if not isinstance(result, list):
        raise ValueError(f"Expected list from {path}, got {type(result).__name__}")
    return result


async def api_get_pagina(path: str, params: dict, pagina: int, limite: int) -> dict:
    """
    Como api_get_many, pero para endpoints paginados: conserva el total de
    resultados que la API calcula junto a la página, en vez de descartarlo.

    El backend solo calcula el total real en la página 1 (en el resto de
    páginas devuelve -1 por coste de la consulta COUNT); por eso aquí se
    normaliza a None fuera de la página 1 en lugar de propagar el -1, que
    induciría a error a quien lo lea.
    """
    response = await _get_client().get(path, params=params, headers=_headers())
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or "datos" not in data:
        raise ValueError(f"Expected paginated dict response from {path}, got {type(data).__name__}")

    resultados = data["datos"]
    total = data.get("total")
    if pagina != 1 or total is None or total < 0:
        total = None

    return {
        "resultados": resultados,
        "pagina": pagina,
        "limite": limite,
        "total": total,
        "hay_mas_resultados": len(resultados) == limite,
    }


async def api_post(path: str, body: dict | None = None) -> dict:
    response = await _get_client().post(path, json=body, headers=_headers())
    if not response.is_success:
        print(f"[api_post] Error {response.status_code} en {path}: {response.text}")
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


async def api_patch(path: str, body: dict | None = None) -> dict:
    response = await _get_client().patch(path, json=body, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


async def api_put(path: str, body: dict | None = None) -> dict:
    response = await _get_client().put(path, json=body, headers=_headers())
    response.raise_for_status()
    data = response.json()
    return data.get("datos", data)


async def api_delete(path: str) -> dict | None:
    response = await _get_client().delete(path, headers=_headers())
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


_CACHE_CAMPOS_FILTRABLES: dict[str, set[str]] = {}


async def campos_filtrables(recurso: str) -> set[str]:
    """
    Campos por los que de verdad se puede filtrar `recurso` (p. ej. "ventas/cliente"),
    según el catálogo real del backend (GET /comun/campos_filtrables) — cacheado en
    memoria del proceso tras la primera consulta por recurso, ya que el esquema de
    campos filtrables no cambia en caliente.
    """
    if recurso not in _CACHE_CAMPOS_FILTRABLES:
        data = await api_get("/comun/campos_filtrables", params={"recurso": recurso})
        if not isinstance(data, dict) or "campos" not in data:
            raise ValueError(f"Respuesta inesperada de /comun/campos_filtrables para {recurso!r}")
        _CACHE_CAMPOS_FILTRABLES[recurso] = set(data["campos"])
    return _CACHE_CAMPOS_FILTRABLES[recurso]


async def clausulas_de_filtro_dinamico(recurso: str, filtro: dict[str, str] | None) -> list:
    """
    Traduce un filtro dinámico {campo: valor} (igualdad exacta) en cláusulas
    [campo, "=", valor], validando cada campo contra campos_filtrables(recurso).
    Lanza ValueError con la lista de campos válidos si alguno no existe, en vez de
    dejarlo llegar tal cual al backend — que no valida nombres de campo
    desconocidos: en el mejor caso falla con un error de SQL, en el peor arma una
    columna sin comprobar a partir de un string que viene de un LLM.
    """
    if not filtro:
        return []
    validos = await campos_filtrables(recurso)
    desconocidos = sorted(set(filtro) - validos)
    if desconocidos:
        raise ValueError(
            f"Campo(s) no filtrable(s) para {recurso}: {', '.join(desconocidos)}. "
            f"Campos válidos: {', '.join(sorted(validos))}"
        )
    return [[campo, "=", valor] for campo, valor in filtro.items()]


def clausula_or_texto(campos: list[str], texto: str) -> dict:
    """
    Cláusula OR que busca `texto` (contiene, case-insensitive) en cualquiera de
    `campos`. Útil cuando quien pregunta no sabe en qué campo concreto está el
    dato (p. ej. "busca a Pérez" sin saber si es el nombre o el email).
    """
    return {"or": [[campo, "~", texto] for campo in campos]}


PERIODOS_VALIDOS = (
    "hoy", "ayer", "mañana",
    "esta_semana", "semana_anterior", "semana_siguiente",
    "este_mes", "mes_anterior", "mes_siguiente",
    "este_año", "año_anterior", "año_siguiente",
)


def resolver_periodo(periodo: str) -> tuple[str, str]:
    """
    Traduce un atajo de periodo relativo a la fecha de hoy en un rango
    (desde, hasta) en formato YYYY-MM-DD. Replica en el servidor los atajos
    de fecha que ya existen en el frontend (rangoDesdeAtajo, packages/lib/src/infraestructura.ts),
    para que el agente de IA no tenga que calcular fechas absolutas a mano.
    """
    hoy = date.today()

    if periodo == "hoy":
        desde = hasta = hoy
    elif periodo == "ayer":
        desde = hasta = hoy - timedelta(days=1)
    elif periodo == "mañana":
        desde = hasta = hoy + timedelta(days=1)
    elif periodo in ("esta_semana", "semana_anterior", "semana_siguiente"):
        offset_dias = {"esta_semana": 0, "semana_anterior": -7, "semana_siguiente": 7}[periodo]
        lunes = hoy - timedelta(days=hoy.isoweekday() - 1) + timedelta(days=offset_dias)
        desde, hasta = lunes, lunes + timedelta(days=6)
    elif periodo in ("este_mes", "mes_anterior", "mes_siguiente"):
        offset_meses = {"este_mes": 0, "mes_anterior": -1, "mes_siguiente": 1}[periodo]
        mes_absoluto = hoy.month - 1 + offset_meses
        anio, mes = hoy.year + mes_absoluto // 12, mes_absoluto % 12 + 1
        desde = date(anio, mes, 1)
        hasta = date(anio, mes, calendar.monthrange(anio, mes)[1])
    elif periodo in ("este_año", "año_anterior", "año_siguiente"):
        offset_anios = {"este_año": 0, "año_anterior": -1, "año_siguiente": 1}[periodo]
        anio = hoy.year + offset_anios
        desde, hasta = date(anio, 1, 1), date(anio, 12, 31)
    else:
        raise ValueError(f"Periodo no reconocido: {periodo!r}. Valores válidos: {', '.join(PERIODOS_VALIDOS)}")

    return desde.isoformat(), hasta.isoformat()