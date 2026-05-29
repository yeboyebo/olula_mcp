from server import mcp
from client import api_get_many


@mcp.tool()
def buscar_prediccion_facturacion_mensual() -> list[dict]:
    """
    Obtiene las predicciones de facturación global mensual.
    """
    return api_get_many("/predicciones/facturacion_global_mensual")


@mcp.tool()
def buscar_prediccion_facturacion_semanal() -> list[dict]:
    """
    Obtiene las predicciones de facturación global semanal.
    """
    return api_get_many("/predicciones/facturacion_global_semanal")


@mcp.tool()
def buscar_metricas_calidad() -> list[dict]:
    """
    Obtiene las métricas de calidad de los modelos de predicción.
    """
    return api_get_many("/predicciones/metricas_calidad")
