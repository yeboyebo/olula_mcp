from server import mcp
from client import api_get_one, api_put


@mcp.tool()
async def obtener_documento_por_codigo(codigo: str) -> dict:
    """
    Obtiene el contenido de un documento por su código.

    Args:
        codigo: Código del documento
    """
    return await api_get_one(f"/documental/documento/contenido_por_codigo/{codigo}")


@mcp.tool()
async def subir_documento(documento_id: str, codigo: str, nombre: str, tipo: str, nombre_fichero: str, versiones: list[dict] | None = None) -> dict:
    """
    Crea o actualiza un documento en el sistema documental.

    Args:
        documento_id: ID del documento
        codigo: Código del documento
        nombre: Nombre del documento
        tipo: Tipo del documento
        nombre_fichero: Nombre del fichero
        versiones: Lista de versiones (opcional)
    """
    body: dict = {
        "id": documento_id,
        "codigo": codigo,
        "nombre": nombre,
        "tipo": tipo,
        "nombre_fichero": nombre_fichero,
    }
    if versiones:
        body["versiones"] = versiones
    return await api_put(f"/documental/documento/{documento_id}", body=body)
