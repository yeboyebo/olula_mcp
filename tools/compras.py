from server import mcp
from client import api_get_one, api_get_pagina, build_query, clausulas_de_filtro_dinamico


@mcp.tool()
async def buscar_proveedor(
    nombre: str | None = None, filtro_extra: dict[str, str] | None = None,
    pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca proveedores por nombre.

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
    filtro.extend(await clausulas_de_filtro_dinamico("compras/proveedor", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/compras/proveedor", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_proveedor(proveedor_id: str) -> dict:
    """
    Obtiene un proveedor por su ID.

    Args:
        proveedor_id: ID del proveedor
    """
    return await api_get_one(f"/compras/proveedor/{proveedor_id}")
