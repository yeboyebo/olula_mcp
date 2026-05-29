from server import mcp
from client import api_get_one, api_get_many, build_query


@mcp.tool()
def buscar_proveedor(nombre: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca proveedores por nombre.

    Args:
        nombre: Filtrar por nombre (parcial)
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get_many("/compras/proveedor", params={"q": q})


@mcp.tool()
def obtener_proveedor(proveedor_id: str) -> dict:
    """
    Obtiene un proveedor por su ID.

    Args:
        proveedor_id: ID del proveedor
    """
    return api_get_one(f"/compras/proveedor/{proveedor_id}")
