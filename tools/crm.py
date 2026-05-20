from server import mcp
from client import api_get, api_post, api_patch, build_query


# ── Leads ─────────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_lead(nombre: str | None = None, estado_id: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca leads (clientes potenciales).

    Args:
        nombre: Filtrar por nombre (parcial)
        estado_id: Filtrar por ID de estado
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    if estado_id:
        filtro.append(["estado_id", "=", estado_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/crm/lead", params={"q": q})


@mcp.tool()
def crear_lead(nombre: str, id_fiscal: str, tipo: str = "cliente", estado_id: str | None = None, responsable_id: str | None = None, email: str | None = None, telefono: str | None = None, fuente_id: str | None = None) -> dict:
    """
    Crea un nuevo lead (cliente potencial).

    Args:
        nombre: Nombre del lead
        id_fiscal: NIF/CIF del lead
        tipo: Tipo de lead (cliente o proveedor)
        estado_id: ID del estado del lead
        responsable_id: ID del responsable
        email: Email del lead
        telefono: Teléfono del lead
        fuente_id: ID de la fuente del lead
    """
    body: dict = {"nombre": nombre, "id_fiscal": id_fiscal, "tipo": tipo}
    if estado_id:
        body["estado_id"] = estado_id
    if responsable_id:
        body["responsable_id"] = responsable_id
    if email:
        body["email"] = email
    if fuente_id:
        body["fuente_id"] = fuente_id
    return api_post("/crm/lead", body=body)


@mcp.tool()
def actualizar_lead(lead_id: str, nombre: str | None = None, email: str | None = None, estado_id: str | None = None) -> dict:
    """
    Actualiza un lead existente.

    Args:
        lead_id: ID del lead
        nombre: Nuevo nombre
        email: Nuevo email
        estado_id: Nuevo estado
    """
    body: dict = {}
    if nombre:
        body["nombre"] = nombre
    if email:
        body["email"] = email
    if estado_id:
        body["estado_id"] = estado_id
    return api_patch(f"/crm/lead/{lead_id}", body=body)


# ── Contactos ─────────────────────────────────────────────────────────────


@mcp.tool()
def buscar_contacto(nombre: str | None = None, email: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca contactos por nombre y/o email.

    Args:
        nombre: Filtrar por nombre (parcial)
        email: Filtrar por email (parcial)
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    if email:
        filtro.append(["email", "~", email])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/crm/contacto", params={"q": q})


@mcp.tool()
def crear_contacto(nombre: str, email: str | None = None, telefono1: str | None = None, nif: str | None = None) -> dict:
    """
    Crea un nuevo contacto.

    Args:
        nombre: Nombre del contacto
        email: Email del contacto
        telefono1: Teléfono del contacto
        nif: NIF del contacto
    """
    body: dict = {"nombre": nombre}
    if email:
        body["email"] = email
    if telefono1:
        body["telefono1"] = telefono1
    if nif:
        body["nif"] = nif
    return api_post("/crm/contacto", body=body)


# ── Oportunidades de venta ────────────────────────────────────────────────


@mcp.tool()
def buscar_oportunidad_venta(descripcion: str | None = None, estado_id: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca oportunidades de venta.

    Args:
        descripcion: Filtrar por descripción (parcial)
        estado_id: Filtrar por ID de estado
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    if estado_id:
        filtro.append(["estado_id", "=", estado_id])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/crm/oportunidad_venta", params={"q": q})


@mcp.tool()
def crear_oportunidad_venta(descripcion: str, nombre_cliente: str, importe: float, estado_id: str, cliente_id: str | None = None, agente_id: str | None = None) -> dict:
    """
    Crea una nueva oportunidad de venta.

    Args:
        descripcion: Descripción de la oportunidad
        nombre_cliente: Nombre del cliente
        importe: Importe de la oportunidad
        estado_id: ID del estado de la oportunidad
        cliente_id: ID del cliente (opcional)
        agente_id: ID del agente comercial
    """
    body: dict = {"descripcion": descripcion, "nombre_cliente": nombre_cliente, "importe": importe, "estado_id": estado_id}
    if cliente_id:
        body["cliente_id"] = cliente_id
    if agente_id:
        body["agente_id"] = agente_id
    return api_post("/crm/oportunidad_venta", body=body)


# ── Incidencias ───────────────────────────────────────────────────────────


@mcp.tool()
def buscar_incidencia(nombre: str | None = None, estado: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca incidencias.

    Args:
        nombre: Filtrar por nombre (parcial)
        estado: Filtrar por estado
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if nombre:
        filtro.append(["nombre", "~", nombre])
    if estado:
        filtro.append(["estado", "=", estado])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/crm/incidencia", params={"q": q})


@mcp.tool()
def crear_incidencia(nombre: str, descripcion: str, prioridad: str = "media", cliente_id: str | None = None) -> dict:
    """
    Crea una nueva incidencia.

    Args:
        nombre: Nombre/título de la incidencia
        descripcion: Descripción detallada
        prioridad: Prioridad (alta, media, baja)
        cliente_id: ID del cliente asociado
    """
    body: dict = {"nombre": nombre, "descripcion": descripcion, "prioridad": prioridad}
    if cliente_id:
        body["cliente_id"] = cliente_id
    return api_post("/crm/incidencia", body=body)


# ── Acciones CRM ──────────────────────────────────────────────────────────


@mcp.tool()
def buscar_accion(descripcion: str | None = None, estado: str | None = None, pagina: int = 1, limite: int = 100) -> list[dict]:
    """
    Busca acciones/actividades del CRM.

    Args:
        descripcion: Filtrar por descripción (parcial)
        estado: Filtrar por estado
        pagina: Número de página
        limite: Resultados por página (máximo 100)
    """
    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    if estado:
        filtro.append(["estado", "=", estado])
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return api_get("/crm/accion", params={"q": q})