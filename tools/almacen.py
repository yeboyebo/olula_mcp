from server import mcp
from client import api_get, api_post, build_query


# ── Artículos ─────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_articulo(descripcion: str | None = None, sku: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca artículos por descripción y/o SKU.

    Args:
        descripcion: Filtrar por descripción (parcial)
        sku: Filtrar por SKU (parcial)
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    if sku:
        filtro.append(["id", "~", sku])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/almacen/articulo", params={"q": q})


@mcp.tool()
def obtener_articulo(articulo_id: str) -> dict:
    """
    Obtiene un artículo por su ID/SKU.

    Args:
        articulo_id: ID del artículo
    """
    return api_get(f"/almacen/articulo/{articulo_id}")


@mcp.tool()
def buscar_tags_articulo(pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca tags de artículos (referencias con precio e IVA).

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    q = build_query(pagina=pagina, limite=limite)
    return api_get("/ventas/articulo/tags", params={"q": q})


# ── Stocks ────────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_stock(articulo_id: str | None = None, almacen_id: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Consulta stocks de artículos por almacén.

    Args:
        articulo_id: Filtrar por ID de artículo
        almacen_id: Filtrar por ID de almacén
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if articulo_id:
        filtro.append(["articulo_id", "=", articulo_id])
    if almacen_id:
        filtro.append(["almacen_id", "=", almacen_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/almacen/stock", params={"q": q})


@mcp.tool()
def obtener_stock(stock_id: str) -> dict:
    """
    Obtiene un registro de stock por su ID.

    Args:
        stock_id: ID del registro de stock
    """
    return api_get(f"/almacen/stock/{stock_id}")


# ── Almacenes ─────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_almacen(nombre: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca almacenes.

    Args:
        nombre: Filtrar por nombre (parcial)
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/almacen/almacen", params={"q": q})


# ── Familias ──────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_familia(descripcion: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca familias de artículos.

    Args:
        descripcion: Filtrar por descripción (parcial)
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/almacen/familia", params={"q": q})


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