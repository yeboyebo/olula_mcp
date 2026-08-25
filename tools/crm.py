from server import mcp
from client import (
    api_get_one, api_get_pagina, api_post, api_patch, build_query,
    clausulas_de_filtro_dinamico, resolver_periodo,
)


# ── Leads ─────────────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_lead(
    nombre: str | None = None, estado_id: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca leads (clientes potenciales).

    Args:
        nombre: Filtrar por nombre (parcial)
        estado_id: Filtrar por ID de estado
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
    if estado_id:
        filtro.append(["estado_id", "=", estado_id])
    filtro.extend(await clausulas_de_filtro_dinamico("crm/lead", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/crm/lead", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def crear_lead(nombre: str, id_fiscal: str, tipo: str = "cliente", estado_id: str | None = None, responsable_id: str | None = None, email: str | None = None, telefono: str | None = None, fuente_id: str | None = None) -> dict:
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
    return await api_post("/crm/lead", body=body)


@mcp.tool()
async def actualizar_lead(lead_id: str, nombre: str | None = None, email: str | None = None, estado_id: str | None = None) -> dict:
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
    return await api_patch(f"/crm/lead/{lead_id}", body=body)


# ── Contactos ─────────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_contacto(
    nombre: str | None = None, email: str | None = None, texto: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca contactos por nombre y/o email.

    Args:
        nombre: Filtrar por nombre (parcial)
        email: Filtrar por email (parcial)
        texto: Búsqueda libre — encuentra el texto en nombre O email a la vez.
            Úsalo cuando no sepas de antemano si lo que te ha dado el usuario
            es un nombre o un email.
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba
            (p. ej. {"nif": "..."} o {"telefono1": "..."}). Si el campo no es
            válido, la tool falla con la lista de campos válidos.
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
    if email:
        filtro.append(["email", "~", email])
    if texto:
        filtro.append({"or": [["nombre", "~", texto], ["email", "~", texto]]})
    filtro.extend(await clausulas_de_filtro_dinamico("crm/contacto", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/crm/contacto", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def crear_contacto(nombre: str, email: str | None = None, telefono1: str | None = None, nif: str | None = None) -> dict:
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
    return await api_post("/crm/contacto", body=body)


# ── Oportunidades de venta ────────────────────────────────────────────────


@mcp.tool()
async def buscar_oportunidad_venta(
    descripcion: str | None = None, estado_id: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca oportunidades de venta.

    Args:
        descripcion: Filtrar por descripción (parcial)
        estado_id: Filtrar por ID de estado
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba
            (p. ej. {"cliente_id": "..."} o {"agente_id": "..."}). Si el campo no
            es válido, la tool falla con la lista de campos válidos.
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    if estado_id:
        filtro.append(["estado_id", "=", estado_id])
    filtro.extend(await clausulas_de_filtro_dinamico("crm/oportunidad_venta", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/crm/oportunidad_venta", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def crear_oportunidad_venta(descripcion: str, nombre_cliente: str, importe: float, estado_id: str, cliente_id: str | None = None, agente_id: str | None = None) -> dict:
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
    body: dict = {"descripcion": descripcion, "nombre_cliente": nombre_cliente,
                  "importe": importe, "estado_id": estado_id}
    if cliente_id:
        body["cliente_id"] = cliente_id
    if agente_id:
        body["agente_id"] = agente_id
    return await api_post("/crm/oportunidad_venta", body=body)


# ── Incidencias ───────────────────────────────────────────────────────────

# La API devuelve/muestra estado y prioridad en minúsculas (snake_case), pero
# la columna real en BD guarda literales en español capitalizados, y el filtro
# de criteria no pasa por la capa de traducción de valores — hay que traducir
# aquí o el filtro no casa nunca con ningún registro.
_ESTADOS_INCIDENCIA = {
    "nueva": "Nueva",
    "en_espera": "Pendiente de Datos",
    "asignada": "Asignada",
    "rechazada": "Rechazada",
    "cerrada": "Cerrada",
}
_PRIORIDADES_INCIDENCIA = {"alta": "Alta", "media": "Media", "baja": "Baja"}


@mcp.tool()
async def buscar_incidencia(
    nombre: str | None = None, estado: str | None = None, prioridad: str | None = None,
    cliente_id: str | None = None, fecha_desde: str | None = None, fecha_hasta: str | None = None,
    periodo: str | None = None, filtro_extra: dict[str, str] | None = None,
    pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca incidencias.

    Args:
        nombre: Filtrar por nombre (parcial)
        estado: Filtrar por estado — uno de: nueva, en_espera, asignada, rechazada,
            cerrada
        prioridad: Filtrar por prioridad — uno de: alta, media, baja
        cliente_id: Filtrar por ID de cliente
        fecha_desde: Filtrar desde esta fecha, inclusive (formato YYYY-MM-DD)
        fecha_hasta: Filtrar hasta esta fecha, inclusive (formato YYYY-MM-DD)
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas.
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba
            (p. ej. {"responsable_id": "..."} o {"proveedor_id": "..."}). Si el
            campo no es válido, la tool falla con la lista de campos válidos.
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
    if estado:
        filtro.append(["estado", "=", _ESTADOS_INCIDENCIA.get(estado.strip().lower(), estado)])
    if prioridad:
        filtro.append(["prioridad", "=", _PRIORIDADES_INCIDENCIA.get(prioridad.strip().lower(), prioridad)])
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    if periodo and not fecha_desde and not fecha_hasta:
        fecha_desde, fecha_hasta = resolver_periodo(periodo)
    if fecha_desde:
        filtro.append(["fecha", ">=", fecha_desde])
    if fecha_hasta:
        filtro.append(["fecha", "<=", fecha_hasta])
    filtro.extend(await clausulas_de_filtro_dinamico("crm/incidencia", filtro_extra))
    q = build_query(filtro or None, orden=["fecha", "DESC"], pagina=pagina, limite=limite)
    return await api_get_pagina("/crm/incidencia", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def crear_incidencia(nombre: str, descripcion: str, prioridad: str = "media", cliente_id: str | None = None) -> dict:
    """
    Crea una nueva incidencia.

    Args:
        nombre: Nombre/título de la incidencia
        descripcion: Descripción detallada
        prioridad: Prioridad (alta, media, baja)
        cliente_id: ID del cliente asociado
    """
    body: dict = {"nombre": nombre,
                  "descripcion": descripcion, "prioridad": prioridad}
    if cliente_id:
        body["cliente_id"] = cliente_id
    return await api_post("/crm/incidencia", body=body)


# ── Acciones CRM ──────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_accion(
    descripcion: str | None = None, estado: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca acciones/actividades del CRM.

    Args:
        descripcion: Filtrar por descripción (parcial)
        estado: Filtrar por estado
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
    if descripcion:
        filtro.append(["descripcion", "~", descripcion])
    if estado:
        filtro.append(["estado", "=", estado])
    filtro.extend(await clausulas_de_filtro_dinamico("crm/accion", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/crm/accion", params={"q": q}, pagina=pagina, limite=limite)
