from server import mcp
from client import api_get_one, api_get_pagina, api_post, build_query, clausulas_de_filtro_dinamico


# ── Artículos ─────────────────────────────────────────────────────────────


"""
@mcp.tool()
def buscar_articulo(descripcion: str | None = None, sku: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    Busca artículos por descripción y/o SKU.

    Args:
        descripcion: Filtrar por descripción (parcial)
        sku: Filtrar por SKU (parcial)
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    if sku:
        filtro.append(["id", "~", sku])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get_many("/almacen/articulo", params={"q": q})

"""
@mcp.tool()
def obtener_articulo_almacen(articulo_id: str) -> dict:
    """
    Obtiene un artículo por su ID/SKU desde el endpoint de almacén
    (/almacen/articulo). Para los datos comerciales del artículo (precio,
    descripción...) usa obtener_articulo, que consulta /ventas/articulo.

    Args:
        articulo_id: ID del artículo
    """
    return api_get_one(f"/almacen/articulo/{articulo_id}")


@mcp.tool()
def buscar_tags_articulo(pagina: int = 1, limite: int = 100) -> dict:
    """
    Busca tags de artículos (referencias con precio e IVA).

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    q = build_query(pagina=pagina, limite=limite)
    return api_get_pagina("/ventas/articulo/tags", params={"q": q}, pagina=pagina, limite=limite)


# ── Stocks ────────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_stock(
    articulo_id: str | None = None, almacen_id: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Consulta stocks de artículos por almacén.

    Args:
        articulo_id: Filtrar por ID de artículo
        almacen_id: Filtrar por ID de almacén
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if articulo_id:
        filtro.append(["articulo_id", "=", articulo_id])
    if almacen_id:
        filtro.append(["almacen_id", "=", almacen_id])
    filtro.extend(clausulas_de_filtro_dinamico("almacen/stock", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get_pagina("/almacen/stock", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
def obtener_stock(stock_id: str) -> dict:
    """
    Obtiene un registro de stock por su ID.

    Args:
        stock_id: ID del registro de stock
    """
    return api_get_one(f"/almacen/stock/{stock_id}")


# ── Almacenes ─────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_almacen(
    nombre: str | None = None, filtro_extra: dict[str, str] | None = None,
    pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca almacenes.

    Args:
        nombre: Filtrar por nombre (parcial)
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    filtro.extend(clausulas_de_filtro_dinamico("almacen/almacen", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get_pagina("/almacen/almacen", params={"q": q}, pagina=pagina, limite=limite)


# ── Familias ──────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_familia(
    descripcion: str | None = None, filtro_extra: dict[str, str] | None = None,
    pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca familias de artículos.

    Args:
        descripcion: Filtrar por descripción (parcial)
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    filtro.extend(clausulas_de_filtro_dinamico("almacen/familia", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get_pagina("/almacen/familia", params={"q": q}, pagina=pagina, limite=limite)


# ── Transferencias ────────────────────────────────────────────────────────


@mcp.tool()
def crear_transferencia(almacen_origen_id: str, almacen_destino_id: str, lineas: list[dict]) -> dict:
    """
    Crea una transferencia de stock entre almacenes.

    Args:
        almacen_origen_id: ID del almacén de origen
        almacen_destino_id: ID del almacén de destino
        lineas: Lista de líneas [{"sku": "...", "cantidad": N}, ...]
    """
    body: dict = {
        "almacen_origen_id": almacen_origen_id,
        "almacen_destino_id": almacen_destino_id,
        "lineas": lineas,
    }
    return api_post("/almacen/transferencia", body=body)
