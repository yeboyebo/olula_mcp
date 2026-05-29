from server import mcp
from client import api_get, api_post, api_patch, build_query


# ── Clientes ──────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_cliente(nombre: str | None = None, email: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca clientes por nombre y/o email. Devuelve una lista de clientes.

    Args:
        nombre: Filtrar por nombre (parcial, case-insensitive)
        email: Filtrar por email
        pagina: Número de página (empieza en 1)
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    if email:
        filtro.append(["email", "~", email])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/ventas/cliente", params={"q": q})


@mcp.tool()
def obtener_cliente(cliente_id: str) -> dict:
    """
    Obtiene un cliente por su ID.

    Args:
        cliente_id: ID del cliente
    """
    return api_get(f"/ventas/cliente/{cliente_id}")


@mcp.tool()
def buscar_cliente_por_email(email: str) -> dict:
    """
    Busca un cliente exactamente por su email.

    Args:
        email: Email del cliente
    """
    return api_get(f"/ventas/cliente/email/{email}")


@mcp.tool()
def crear_cliente(nombre: str, id_fiscal: str, tipo_id_fiscal: str = "NIF", empresa_id: str | None = None, agente_id: str | None = None, email: str | None = None, telefono1: str | None = None) -> dict:
    """
    Crea un nuevo cliente.

    Args:
        nombre: Nombre del cliente
        id_fiscal: NIF/CIF del cliente
        tipo_id_fiscal: Tipo de identificación fiscal (NIF, CIF, etc.)
        empresa_id: ID de la empresa asociada
        agente_id: ID del agente comercial asignado
        email: Email del cliente
        telefono1: Teléfono del cliente
    """
    body: dict = {"nombre": nombre, "id_fiscal":  id_fiscal, "tipo_id_fiscal": tipo_id_fiscal}
    if empresa_id:
        body["empresa_id"] = empresa_id
    if agente_id:
        body["agente_id"] = agente_id
    if email:
        body["email"] = email
    if telefono1:
        body["telefono1"] = telefono1
    return api_post("/ventas/cliente", body=body)


@mcp.tool()
def actualizar_cliente(cliente_id: str, nombre: str | None = None, email: str | None = None, telefono1: str | None = None, observaciones: str | None = None) -> dict:
    """
    Actualiza los datos de un cliente existente.

    Args:
        cliente_id: ID del cliente a actualizar
        nombre: Nuevo nombre
        email: Nuevo email
        telefono1: Nuevo teléfono
        observaciones: Nuevas observaciones
    """
    body: dict = {}
    if nombre:
        body["nombre"] = nombre
    if email:
        body["email"] = email
    if telefono1:
        body["telefono1"] = telefono1
    if observaciones:
        body["observaciones"] = observaciones
    return api_patch(f"/ventas/cliente/{cliente_id}", body=body)


# ── Presupuestos ──────────────────────────────────────────────────────────


@mcp.tool()
def buscar_presupuesto(pagina: int = 1, limite: int = 100, cliente_id: str | None = None) -> list[dict]:
    """
    Busca presupuestos de venta. Devuelve una lista de presupuestos.

    Args:
        pagina: Número de página (empieza en 1)
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/ventas/presupuesto", params={"q": q})


@mcp.tool()
def obtener_presupuesto(presupuesto_id: str) -> dict:
    """
    Obtiene un presupuesto por su ID.

    Args:
        presupuesto_id: ID del presupuesto
    """
    return api_get(f"/ventas/presupuesto/{presupuesto_id}")


@mcp.tool()
def crear_presupuesto(empresa_id: str, cliente: dict, lineas: list[dict]) -> dict:
    """
    Crea un presupuesto de venta. El cliente puede ser: {"email": "..."} para buscar por email,
    {"cliente_id": "...", "direccion_id": "..."} para un cliente registrado,
    o {"nombre": "...", "id_fiscal": "..."} para un cliente no registrado.

    Args:
        empresa_id: ID de la empresa
        cliente: Datos del cliente (ver formatos arriba)
        lineas: Lista de líneas [{"articulo_id": "...", "cantidad": N}, ...]
    """
    body: dict = {"empresa_id": empresa_id, "cliente": cliente, "lineas": lineas}
    return api_post("/ventas/presupuesto", body=body)


@mcp.tool()
def aprobar_presupuesto(presupuesto_id: str) -> dict:
    """
    Aprueba un presupuesto de venta, convirtiéndolo en un pedido.

    Args:
        presupuesto_id: ID del presupuesto a aprobar
    """
    return api_patch(f"/ventas/presupuesto/{presupuesto_id}/aprobar")


# ── Pedidos ───────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_pedido(pagina: int = 1, limite: int = 100, cliente_id: str | None = None) -> list[dict]:
    """
    Busca pedidos de venta.

    Args:
        pagina: Número de página (empieza en 1)
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/ventas/pedido", params={"q": q})


@mcp.tool()
def crear_pedido(empresa_id: str, cliente: dict, lineas: list[dict]) -> dict:
    """
    Crea un pedido de venta.

    Args:
        empresa_id: ID de la empresa
        cliente: Datos del cliente (mismos formatos que crear_presupuesto)
        lineas: Lista de líneas [{"articulo_id": "...", "cantidad": N}, ...]
    """
    body: dict = {"empresa_id": empresa_id, "cliente": cliente, "lineas": lineas}
    return api_post("/ventas/pedido", body=body)


# ── Albaranes ─────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_albaran(pagina: int = 1, limite: int = 100, cliente_id: str | None = None) -> list[dict]:
    """
    Busca albaranes de venta.

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/ventas/albaran", params={"q": q})


# ── Facturas ──────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_factura(pagina: int = 1, limite: int = 100, cliente_id: str | None = None) -> list[dict]:
    """
    Busca facturas de venta.

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/ventas/factura", params={"q": q})


@mcp.tool()
def obtener_factura(factura_id: str) -> dict:
    """
    Obtiene una factura por su ID.

    Args:
        factura_id: ID de la factura
    """
    return api_get(f"/ventas/factura/{factura_id}")


@mcp.tool()
def crear_factura(empresa_id: str, cliente: dict, lineas: list[dict]) -> dict:
    """
    Crea una factura de venta.

    Args:
        empresa_id: ID de la empresa
        cliente: Datos del cliente (mismos formatos que crear_presupuesto)
        lineas: Lista de líneas [{"articulo_id": "...", "cantidad": N}, ...]
    """
    body: dict = {"empresa_id": empresa_id, "cliente": cliente, "lineas": lineas}
    return api_post("/ventas/factura", body=body)


@mcp.tool()
def emitir_factura(factura_id: str) -> dict:
    """
    Emite una factura de venta.

    Args:
        factura_id: ID de la factura a emitir
    """
    return api_patch(f"/ventas/factura/{factura_id}/emitir")