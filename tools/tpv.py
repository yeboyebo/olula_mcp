from server import mcp
from client import api_get_one, api_get_many, api_post, api_patch, build_query


# ── Ventas TPV ────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_venta_tpv(pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca ventas del punto de venta (TPV).

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    q = build_query(pagina=pagina, limite=limite)
    return api_get_many("/tpv/venta", params={"q": q})


@mcp.tool()
def crear_venta_tpv(agente_id: str, punto_venta_id: str, cliente: dict | None = None) -> dict:
    """
    Crea una nueva venta en el TPV.

    Args:
        agente_id: ID del agente/vendedor
        punto_venta_id: ID del punto de venta
        cliente: Datos del cliente (opcional). Formato: {"cliente_id": "..."} para registrado
    """
    body: dict = {"agente_id": agente_id, "punto_venta_id": punto_venta_id}
    if cliente:
        body["cliente"] = cliente
    return api_post("/tpv/venta", body=body)


@mcp.tool()
def agregar_linea_venta_tpv(venta_id: str, articulo_id: str, cantidad: float) -> dict:
    """
    Agrega una línea de artículo a una venta TPV existente.

    Args:
        venta_id: ID de la venta
        articulo_id: ID del artículo
        cantidad: Cantidad
    """
    body = {"articulo_id": articulo_id, "cantidad": cantidad}
    return api_post(f"/tpv/venta/{venta_id}/linea", body=body)


@mcp.tool()
def agregar_linea_venta_tpv_barcode(venta_id: str, barcode: str, cantidad: float = 1) -> dict:
    """
    Agrega una línea a una venta TPV escaneando un código de barras.

    Args:
        venta_id: ID de la venta
        barcode: Código de barras del artículo
        cantidad: Cantidad (por defecto 1)
    """
    body = {"barcode": barcode, "cantidad": cantidad}
    return api_post(f"/tpv/venta/{venta_id}/linea_por_barcode", body=body)


@mcp.tool()
def agregar_pago_tpv(venta_id: str, importe: float, forma_pago: str, punto_venta_id: str | None = None, vale_id: str | None = None) -> dict:
    """
    Agrega un pago a una venta TPV.

    Args:
        venta_id: ID de la venta
        importe: Importe del pago
        forma_pago: Forma de pago (efectivo, tarjeta, vale)
        punto_venta_id: ID del punto de venta
        vale_id: ID del vale (si forma de pago es vale)
    """
    body: dict = {"importe": importe, "forma_pago": forma_pago}
    if punto_venta_id:
        body["punto_venta_id"] = punto_venta_id
    if vale_id:
        body["vale_id"] = vale_id
    return api_post(f"/tpv/venta/{venta_id}/pago", body=body)


@mcp.tool()
def emitir_venta_tpv(venta_id: str) -> dict:
    """
    Emite/finaliza una venta TPV.

    Args:
        venta_id: ID de la venta a emitir
    """
    return api_patch(f"/tpv/venta/{venta_id}/emitir")


# ── Arqueos ───────────────────────────────────────────────────────────────


@mcp.tool()
def crear_arqueo(punto_venta_id: str, agente_id: str) -> dict:
    """
    Crea un nuevo arqueo de caja (apertura).

    Args:
        punto_venta_id: ID del punto de venta
        agente_id: ID del agente que abre la caja
    """
    body = {"punto_venta_id": punto_venta_id, "agente_id": agente_id}
    return api_post("/tpv/arqueo", body=body)


@mcp.tool()
def cerrar_arqueo(arqueo_id: str, agente_id: str, movimiento_cierre: float) -> dict:
    """
    Cierra un arqueo de caja.

    Args:
        arqueo_id: ID del arqueo
        agente_id: ID del agente que cierra
        movimiento_cierre: Importe del movimiento de cierre
    """
    body = {"agente_id": agente_id, "movimiento_cierre": movimiento_cierre}
    return api_patch(f"/tpv/arqueo/{arqueo_id}/cerrar", body=body)
