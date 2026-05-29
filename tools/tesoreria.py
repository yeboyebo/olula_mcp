from server import mcp
from client import api_get_many, api_get_one, build_query


@mcp.tool()
def buscar_recibo(factura_id: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca recibos de venta.

    Args:
        factura_id: Filtrar por ID de factura
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if factura_id:
        filtro.append(["factura_id", "=", factura_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get_many("/tesoreria/recibo_venta", params={"q": q})


@mcp.tool()
def obtener_recibo(recibo_id: str) -> dict:
    """
    Obtiene un recibo por su ID.

    Args:
        recibo_id: ID del recibo
    """
    return api_get_one(f"/tesoreria/recibo_venta/{recibo_id}")
