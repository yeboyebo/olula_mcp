from server import mcp
from client import (
    api_get_one, api_get_pagina, api_post, api_patch, build_query,
    clausulas_de_filtro_dinamico, resolver_periodo,
)
from tools.tipos import ClienteRegistrado


# ── Ventas TPV ────────────────────────────────────────────────────────────

_ORDENES_VENTA_TPV = {
    "fecha_asc": ["fecha", "ASC"],
    "fecha_desc": ["fecha", "DESC"],
    "total_asc": ["total", "ASC"],
    "total_desc": ["total", "DESC"],
    "codigo_asc": ["codigo", "ASC"],
    "codigo_desc": ["codigo", "DESC"],
}


def _resolver_orden_venta_tpv(orden: str | None) -> list:
    if orden is None:
        return _ORDENES_VENTA_TPV["fecha_desc"]
    clave = orden.strip().lower()
    if clave not in _ORDENES_VENTA_TPV:
        raise ValueError(
            f"orden no reconocido: {orden!r}. Valores válidos: {', '.join(_ORDENES_VENTA_TPV)}"
        )
    return _ORDENES_VENTA_TPV[clave]


@mcp.tool()
async def buscar_venta_tpv(
    pagina: int = 1, limite: int = 100, cliente_id: str | None = None,
    agente_id: str | None = None, punto_venta_id: str | None = None,
    fecha_desde: str | None = None, fecha_hasta: str | None = None, periodo: str | None = None,
    codigo: str | None = None, orden: str | None = None,
    filtro_extra: dict[str, str] | None = None,
) -> dict:
    """
    Busca ventas del punto de venta (TPV).

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
        agente_id: Filtrar por ID del agente/vendedor que hizo la venta
        punto_venta_id: Filtrar por ID del punto de venta/caja
        fecha_desde: Filtrar desde esta fecha, inclusive (formato YYYY-MM-DD)
        fecha_hasta: Filtrar hasta esta fecha, inclusive (formato YYYY-MM-DD)
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas. Útil para
            "las ventas de hoy" o "las ventas de este mes" sin calcular fechas a mano.
        codigo: Filtrar por número/código de venta (coincidencia parcial)
        orden: Orden de los resultados — uno de: fecha_asc, fecha_desc, total_asc,
            total_desc, codigo_asc, codigo_desc. Por defecto "fecha_desc" (las más
            recientes primero).
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    if agente_id:
        filtro.append(["agente_id", "=", agente_id])
    if punto_venta_id:
        filtro.append(["punto_venta_id", "=", punto_venta_id])
    if periodo and not fecha_desde and not fecha_hasta:
        fecha_desde, fecha_hasta = resolver_periodo(periodo)
    if fecha_desde:
        filtro.append(["fecha", ">=", fecha_desde])
    if fecha_hasta:
        filtro.append(["fecha", "<=", fecha_hasta])
    if codigo:
        filtro.append(["codigo", "~", codigo])
    filtro.extend(await clausulas_de_filtro_dinamico("tpv/venta", filtro_extra))
    q = build_query(filtro or None, orden=_resolver_orden_venta_tpv(orden), pagina=pagina, limite=limite)
    return await api_get_pagina("/tpv/venta", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def crear_venta_tpv(agente_id: str, punto_venta_id: str, cliente: ClienteRegistrado | None = None) -> dict:
    """
    Crea una nueva venta en el TPV.

    Args:
        agente_id: ID del agente/vendedor
        punto_venta_id: ID del punto de venta
        cliente: Datos del cliente (opcional). Formato: {"cliente_id": "..."} para registrado
    """
    body: dict = {"agente_id": agente_id, "punto_venta_id": punto_venta_id}
    if cliente:
        body["cliente"] = cliente
    return await api_post("/tpv/venta", body=body)


@mcp.tool()
async def agregar_linea_venta_tpv(venta_id: str, articulo_id: str, cantidad: float) -> dict:
    """
    Agrega una línea de artículo a una venta TPV existente.

    Args:
        venta_id: ID de la venta
        articulo_id: ID del artículo
        cantidad: Cantidad
    """
    body = {"articulo_id": articulo_id, "cantidad": cantidad}
    return await api_post(f"/tpv/venta/{venta_id}/linea", body=body)


@mcp.tool()
async def agregar_linea_venta_tpv_barcode(venta_id: str, barcode: str, cantidad: float = 1) -> dict:
    """
    Agrega una línea a una venta TPV escaneando un código de barras.

    Args:
        venta_id: ID de la venta
        barcode: Código de barras del artículo
        cantidad: Cantidad (por defecto 1)
    """
    body = {"barcode": barcode, "cantidad": cantidad}
    return await api_post(f"/tpv/venta/{venta_id}/linea_por_barcode", body=body)


@mcp.tool()
async def agregar_pago_tpv(venta_id: str, importe: float, forma_pago: str, punto_venta_id: str | None = None, vale_id: str | None = None) -> dict:
    """
    Agrega un pago a una venta TPV.

    Args:
        venta_id: ID de la venta
        importe: Importe del pago
        forma_pago: Forma de pago (efectivo, tarjeta, vale)
        punto_venta_id: ID del punto de venta
        vale_id: ID del vale (si forma de pago es vale)
    """
    body: dict = {"importe": importe, "forma_pago": forma_pago}
    if punto_venta_id:
        body["punto_venta_id"] = punto_venta_id
    if vale_id:
        body["vale_id"] = vale_id
    return await api_post(f"/tpv/venta/{venta_id}/pago", body=body)


@mcp.tool()
async def emitir_venta_tpv(venta_id: str) -> dict:
    """
    Emite/finaliza una venta TPV.

    Args:
        venta_id: ID de la venta a emitir
    """
    return await api_patch(f"/tpv/venta/{venta_id}/emitir")


# ── Arqueos ───────────────────────────────────────────────────────────────


@mcp.tool()
async def crear_arqueo(punto_venta_id: str, agente_id: str) -> dict:
    """
    Crea un nuevo arqueo de caja (apertura).

    Args:
        punto_venta_id: ID del punto de venta
        agente_id: ID del agente que abre la caja
    """
    body = {"punto_venta_id": punto_venta_id, "agente_id": agente_id}
    return await api_post("/tpv/arqueo", body=body)


@mcp.tool()
async def cerrar_arqueo(arqueo_id: str, agente_id: str, movimiento_cierre: float) -> dict:
    """
    Cierra un arqueo de caja.

    Args:
        arqueo_id: ID del arqueo
        agente_id: ID del agente que cierra
        movimiento_cierre: Importe del movimiento de cierre
    """
    body = {"agente_id": agente_id, "movimiento_cierre": movimiento_cierre}
    return await api_patch(f"/tpv/arqueo/{arqueo_id}/cerrar", body=body)
