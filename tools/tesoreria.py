from server import mcp
from client import api_get_one, api_get_pagina, build_query, clausulas_de_filtro_dinamico, resolver_periodo

# La API no traduce el estado del recibo (a diferencia de crm.incidencia); los
# literales de BD son estos tal cual, en español y capitalizados.
_ESTADOS_RECIBO = {"pendiente": "Emitido", "cobrado": "Pagado", "devuelto": "Devuelto"}


@mcp.tool()
def buscar_recibo(
    factura_id: str | None = None, cliente_id: str | None = None, estado: str | None = None,
    fecha_desde: str | None = None, fecha_hasta: str | None = None, periodo: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca recibos de venta.

    Args:
        factura_id: Filtrar por ID de factura
        cliente_id: Filtrar por ID de cliente
        estado: Filtrar por estado — uno de: pendiente, cobrado, devuelto
        fecha_desde: Filtrar por fecha de emisión desde esta fecha, inclusive
            (formato YYYY-MM-DD)
        fecha_hasta: Filtrar por fecha de emisión hasta esta fecha, inclusive
            (formato YYYY-MM-DD)
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas.
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba
            (p. ej. {"fecha_vencimiento": "..."} o {"id_fiscal": "..."}). Si el
            campo no es válido, la tool falla con la lista de campos válidos.
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if factura_id:
        filtro.append(["idfactura", "=", factura_id])
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    if estado:
        filtro.append(["estado", "=", _ESTADOS_RECIBO.get(estado.strip().lower(), estado)])
    if periodo and not fecha_desde and not fecha_hasta:
        fecha_desde, fecha_hasta = resolver_periodo(periodo)
    if fecha_desde:
        filtro.append(["fecha_emision", ">=", fecha_desde])
    if fecha_hasta:
        filtro.append(["fecha_emision", "<=", fecha_hasta])
    filtro.extend(clausulas_de_filtro_dinamico("tesoreria/recibo_venta", filtro_extra))
    q = build_query(filtro or None, orden=["fecha_emision", "DESC"], pagina=pagina, limite=limite)
    return api_get_pagina("/tesoreria/recibo_venta", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
def obtener_recibo(recibo_id: str) -> dict:
    """
    Obtiene un recibo por su ID.

    Args:
        recibo_id: ID del recibo
    """
    return api_get_one(f"/tesoreria/recibo_venta/{recibo_id}")
