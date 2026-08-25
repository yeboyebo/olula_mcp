from server import mcp
from client import api_get_many


@mcp.tool()
async def buscar_prediccion_facturacion_mensual() -> list[dict]:
    """
    Obtiene las predicciones de facturación global mensual.
    """
    return await api_get_many("/predicciones/facturacion_global_mensual")


@mcp.tool()
async def buscar_prediccion_facturacion_semanal() -> list[dict]:
    """
    Obtiene las predicciones de facturación global semanal.
    """
    return await api_get_many("/predicciones/facturacion_global_semanal")


@mcp.tool()
async def buscar_metricas_calidad() -> list[dict]:
    """
    Obtiene las métricas de calidad de los modelos de predicción.
    """
    return await api_get_many("/predicciones/metricas_calidad")
