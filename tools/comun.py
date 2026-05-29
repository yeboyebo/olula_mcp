from server import mcp
from client import api_get_one, api_get_many


@mcp.tool()
def obtener_empresa(empresa_id: str | None = None) -> dict | list[dict]:
    """
    Obtiene empresas. Si se proporciona empresa_id, devuelve una empresa concreta.

    Args:
        empresa_id: ID de la empresa (opcional)
    """
    if empresa_id:
        return api_get_one(f"/comun/empresa/{empresa_id}")
    return api_get_many("/comun/empresa")


@mcp.tool()
def buscar_divisa() -> list[dict]:
    """
    Obtiene las divisas disponibles.
    """
    return api_get_many("/comun/divisa")


@mcp.tool()
def buscar_forma_pago() -> list[dict]:
    """
    Obtiene las formas de pago disponibles.
    """
    return api_get_many("/cache/comun/formapago")


@mcp.tool()
def buscar_pais() -> list[dict]:
    """
    Obtiene los países disponibles.
    """
    return api_get_many("/comun/pais")
