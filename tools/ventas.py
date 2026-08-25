from server import mcp
from client import (
    api_get_one, api_get_pagina, api_post, api_patch, build_query,
    clausula_or_texto, clausulas_de_filtro_dinamico, resolver_periodo,
)
from tools.tipos import ClienteVenta, LineaVenta


# ── Artículos ─────────────────────────────────────────────────────────────

@mcp.tool()
async def buscar_articulo(
    descripcion: str | None = None, sku: str | None = None, texto: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca artículos por descripción y/o SKU.

    Args:
        descripcion: Filtrar por descripción (parcial)
        sku: Filtrar por SKU (parcial)
        texto: Búsqueda libre — encuentra el texto en descripción O SKU a la
            vez. Úsalo cuando no sepas de antemano si lo que busca el usuario
            es la descripción o el código.
        filtro_extra: Filtro EXACTO por cualquier otro campo del artículo que no
            esté arriba (p. ej. {"familia_id": "..."}). Usa el nombre de campo
            que mejor describa el dato — si no es válido, la tool falla con la
            lista de campos válidos para que puedas reintentar con uno de esos.
        pagina: Número de página
        limite: Resultados por página (máximo 100)

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1
        (el backend no recalcula el conteo en el resto de páginas); usa
        "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if descripcion:
        # El campo filtrable real es "nombre" (así lo expone dict_criteria de
        # ventas/articulo en el backend), aunque el campo de RESPUESTA del artículo
        # se llame "descripcion" — filtrar por "descripcion" nunca casaba con nada.
        filtro.append(["nombre", "~", descripcion])
    if sku:
        filtro.append(["id", "~", sku])
    if texto:
        filtro.append(clausula_or_texto(["nombre", "id"], texto))
    filtro.extend(await clausulas_de_filtro_dinamico(
        "ventas/articulo", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/ventas/articulo", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_articulo(articulo_id: str) -> dict:
    """
    Obtiene un artículo por su ID/SKU.

    Args:
        articulo_id: ID del artículo
    """
    return await api_get_one(f"/ventas/articulo/{articulo_id}")

# ── Clientes ──────────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_cliente(
    nombre: str | None = None, email: str | None = None, texto: str | None = None,
    filtro_extra: dict[str, str] | None = None, pagina: int = 1, limite: int = 100,
) -> dict:
    """
    Busca clientes por nombre y/o email. Devuelve una lista de clientes.

    Args:
        nombre: Filtrar por nombre (parcial, case-insensitive)
        email: Filtrar por email
        texto: Búsqueda libre — encuentra el texto en nombre O email a la vez.
            Úsalo cuando no sepas de antemano si lo que te ha dado el usuario
            es un nombre o un email.
        filtro_extra: Filtro EXACTO por cualquier otro dato preciso de
            identificación que el usuario haya dado y que no sea nombre/email
            (p. ej. {"id_fiscal": "74510345M"} para CIF/NIF, {"telefono1": "..."}
            para teléfono). Úsalo SIEMPRE que tengas un dato exacto como este en
            vez de meterlo en `texto`/`nombre` — evita una búsqueda difusa que
            puede devolver homónimos sin incluir siquiera al cliente correcto. Si
            el campo no es válido, la tool falla con la lista de campos válidos.
        pagina: Número de página (empieza en 1)
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
        filtro.append(clausula_or_texto(["nombre", "email"], texto))
    filtro.extend(await clausulas_de_filtro_dinamico("ventas/cliente", filtro_extra))
    q = build_query(filtro or None, pagina=pagina, limite=limite)
    return await api_get_pagina("/ventas/cliente", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_cliente(cliente_id: str) -> dict:
    """
    Obtiene un cliente por su ID.

    Args:
        cliente_id: ID del cliente
    """
    return await api_get_one(f"/ventas/cliente/{cliente_id}")


@mcp.tool()
async def buscar_cliente_por_email(email: str) -> dict:
    """
    Busca un cliente exactamente por su email.

    Args:
        email: Email del cliente
    """
    return await api_get_one(f"/ventas/cliente/email/{email}")


@mcp.tool()
async def crear_cliente(nombre: str, id_fiscal: str, tipo_id_fiscal: str = "NIF", empresa_id: str | None = None, agente_id: str | None = None, email: str | None = None, telefono1: str | None = None) -> dict:
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
    body: dict = {"nombre": nombre, "id_fiscal":  id_fiscal,
                  "tipo_id_fiscal": tipo_id_fiscal}
    if empresa_id:
        body["empresa_id"] = empresa_id
    if agente_id:
        body["agente_id"] = agente_id
    if email:
        body["email"] = email
    if telefono1:
        body["telefono1"] = telefono1
    return await api_post("/ventas/cliente", body=body)


@mcp.tool()
async def actualizar_cliente(cliente_id: str, nombre: str | None = None, email: str | None = None, telefono1: str | None = None, observaciones: str | None = None) -> dict:
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
    return await api_patch(f"/ventas/cliente/{cliente_id}", body=body)


# ── Ayudas comunes de fecha/orden para documentos de venta ─────────────────

_ORDENES_DOCUMENTO_VENTA = {
    "fecha_asc": ["fecha", "ASC"],
    "fecha_desc": ["fecha", "DESC"],
    "total_asc": ["total", "ASC"],
    "total_desc": ["total", "DESC"],
    "codigo_asc": ["codigo", "ASC"],
    "codigo_desc": ["codigo", "DESC"],
}


def _resolver_orden_documento_venta(orden: str | None) -> list:
    if orden is None:
        return _ORDENES_DOCUMENTO_VENTA["fecha_desc"]
    clave = orden.strip().lower()
    if clave not in _ORDENES_DOCUMENTO_VENTA:
        raise ValueError(
            f"orden no reconocido: {orden!r}. Valores válidos: {', '.join(_ORDENES_DOCUMENTO_VENTA)}"
        )
    return _ORDENES_DOCUMENTO_VENTA[clave]


def _aplicar_periodo(filtro: list, campo_fecha: str, periodo: str | None, fecha_desde: str | None, fecha_hasta: str | None) -> tuple[str | None, str | None]:
    if periodo and not fecha_desde and not fecha_hasta:
        fecha_desde, fecha_hasta = resolver_periodo(periodo)
    if fecha_desde:
        filtro.append([campo_fecha, ">=", fecha_desde])
    if fecha_hasta:
        filtro.append([campo_fecha, "<=", fecha_hasta])
    return fecha_desde, fecha_hasta


# ── Presupuestos ──────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_presupuesto(
    pagina: int = 1, limite: int = 100, cliente_id: str | None = None,
    fecha_desde: str | None = None, fecha_hasta: str | None = None, periodo: str | None = None,
    codigo: str | None = None, total_minimo: float | None = None,
    total_maximo: float | None = None, aprobado: bool | None = None, orden: str | None = None,
    filtro_extra: dict[str, str] | None = None,
) -> dict:
    """
    Busca presupuestos de venta. Devuelve una lista de presupuestos.

    Args:
        pagina: Número de página (empieza en 1)
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
        fecha_desde: Filtrar desde esta fecha, inclusive (formato YYYY-MM-DD)
        fecha_hasta: Filtrar hasta esta fecha, inclusive (formato YYYY-MM-DD)
        codigo: Filtrar por número/código de presupuesto (coincidencia parcial, p. ej.
            "0001" encuentra "PRESUPUESTO-0001") — usa esto cuando el usuario
            mencione el número de un presupuesto concreto
        total_minimo: Filtrar presupuestos con importe total igual o superior
        total_maximo: Filtrar presupuestos con importe total igual o inferior
        aprobado: Filtrar por si el presupuesto ya ha sido aprobado (convertido en
            pedido) o no
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas.
        orden: Orden de los resultados — uno de: fecha_asc, fecha_desc, total_asc,
            total_desc, codigo_asc, codigo_desc. Por defecto "fecha_desc" (los más
            recientes primero), para que preguntas como "el último presupuesto de
            este cliente" no dependan de que esté entre los primeros de una página
            sin ordenar.
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    _aplicar_periodo(filtro, "fecha", periodo, fecha_desde, fecha_hasta)
    if codigo:
        filtro.append(["codigo", "~", codigo])
    if total_minimo is not None:
        filtro.append(["total", ">=", total_minimo])
    if total_maximo is not None:
        filtro.append(["total", "<=", total_maximo])
    if aprobado is not None:
        # "aprobado" de cara al usuario es lo inverso de la columna real "editable"
        filtro.append(["editable", "=", not aprobado])
    filtro.extend(await clausulas_de_filtro_dinamico(
        "ventas/presupuesto", filtro_extra))
    q = build_query(filtro or None, orden=_resolver_orden_documento_venta(
        orden), pagina=pagina, limite=limite)
    return await api_get_pagina("/ventas/presupuesto", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_presupuesto(presupuesto_id: str) -> dict:
    """
    Obtiene un presupuesto por su ID.

    Args:
        presupuesto_id: ID del presupuesto
    """
    return await api_get_one(f"/ventas/presupuesto/{presupuesto_id}")


@mcp.tool()
async def crear_presupuesto(empresa_id: str, cliente: ClienteVenta, lineas: list[LineaVenta]) -> dict:
    """
    Crea un presupuesto de venta. El cliente puede ser: {"email": "..."} para buscar por email,
    {"cliente_id": "...", "direccion_id": "..."} para un cliente registrado,
    o {"nombre": "...", "id_fiscal": "..."} para un cliente no registrado.

    Args:
        empresa_id: ID de la empresa
        cliente: Datos del cliente (ver formatos arriba)
        lineas: Lista de líneas [{"articulo": {"articulo_id": "..."}, "cantidad": N}, ...].
            Para una línea sin artículo de catálogo, usa
            {"articulo": {"descripcion": "...", "pvp_unitario": N}, "cantidad": N}.
    """
    body: dict = {"empresa_id": empresa_id,
                  "cliente": cliente, "lineas": lineas}
    return await api_post("/ventas/presupuesto", body=body)


@mcp.tool()
async def aprobar_presupuesto(presupuesto_id: str) -> dict:
    """
    Aprueba un presupuesto de venta, convirtiéndolo en un pedido.

    Args:
        presupuesto_id: ID del presupuesto a aprobar
    """
    return await api_patch(f"/ventas/presupuesto/{presupuesto_id}/aprobar")


# ── Pedidos ───────────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_pedido(
    pagina: int = 1, limite: int = 100, cliente_id: str | None = None,
    fecha_desde: str | None = None, fecha_hasta: str | None = None, periodo: str | None = None,
    codigo: str | None = None, total_minimo: float | None = None,
    total_maximo: float | None = None, estado_servido: str | None = None, orden: str | None = None,
    filtro_extra: dict[str, str] | None = None,
) -> dict:
    """
    Busca pedidos de venta.

    Args:
        pagina: Número de página (empieza en 1)
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
        fecha_desde: Filtrar desde esta fecha, inclusive (formato YYYY-MM-DD)
        fecha_hasta: Filtrar hasta esta fecha, inclusive (formato YYYY-MM-DD)
        codigo: Filtrar por número/código de pedido (coincidencia parcial, p. ej.
            "0001" encuentra "PEDIDO-0001") — usa esto cuando el usuario mencione el
            número de un pedido concreto
        total_minimo: Filtrar pedidos con importe total igual o superior
        total_maximo: Filtrar pedidos con importe total igual o inferior
        estado_servido: Filtrar por estado de entrega — uno de "pendiente", "parcial"
            o "total"
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas.
        orden: Orden de los resultados — uno de: fecha_asc, fecha_desc, total_asc,
            total_desc, codigo_asc, codigo_desc. Por defecto "fecha_desc" (los más
            recientes primero), para que preguntas como "el último pedido de este
            cliente" no dependan de que esté entre los primeros de una página sin
            ordenar.
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    _aplicar_periodo(filtro, "fecha", periodo, fecha_desde, fecha_hasta)
    if codigo:
        filtro.append(["codigo", "~", codigo])
    if total_minimo is not None:
        filtro.append(["total", ">=", total_minimo])
    if total_maximo is not None:
        filtro.append(["total", "<=", total_maximo])
    if estado_servido:
        # La columna real solo acepta los literales en español usados por la app
        valores_servido = {"pendiente": "No",
                           "parcial": "Parcial", "total": "Sí"}
        filtro.append(["servido", "=", valores_servido.get(
            estado_servido.strip().lower(), estado_servido)])
    filtro.extend(await clausulas_de_filtro_dinamico("ventas/pedido", filtro_extra))
    q = build_query(filtro or None, orden=_resolver_orden_documento_venta(
        orden), pagina=pagina, limite=limite)
    return await api_get_pagina("/ventas/pedido", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_pedido(pedido_id: str) -> dict:
    """
    Obtiene un pedido por su ID.

    Args:
        pedido_id: ID del pedido
    """
    return await api_get_one(f"/ventas/pedido/{pedido_id}")


@mcp.tool()
async def crear_pedido(empresa_id: str, cliente: ClienteVenta, lineas: list[LineaVenta]) -> dict:
    """
    Crea un pedido de venta.

    Args:
        empresa_id: ID de la empresa
        cliente: Datos del cliente (mismos formatos que crear_presupuesto)
        lineas: Lista de líneas [{"articulo": {"articulo_id": "..."}, "cantidad": N}, ...].
            Para una línea sin artículo de catálogo, usa
            {"articulo": {"descripcion": "...", "pvp_unitario": N}, "cantidad": N}.
    """
    body: dict = {"empresa_id": empresa_id,
                  "cliente": cliente, "lineas": lineas}
    return await api_post("/ventas/pedido", body=body)


# ── Albaranes ─────────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_albaran(
    pagina: int = 1, limite: int = 100, cliente_id: str | None = None,
    fecha_desde: str | None = None, fecha_hasta: str | None = None, periodo: str | None = None,
    codigo: str | None = None, total_minimo: float | None = None,
    total_maximo: float | None = None, facturado: bool | None = None, orden: str | None = None,
    filtro_extra: dict[str, str] | None = None,
) -> dict:
    """
    Busca albaranes de venta.

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
        fecha_desde: Filtrar desde esta fecha, inclusive (formato YYYY-MM-DD)
        fecha_hasta: Filtrar hasta esta fecha, inclusive (formato YYYY-MM-DD)
        codigo: Filtrar por número/código de albarán (coincidencia parcial, p. ej.
            "0001" encuentra "ALBARAN-0001") — usa esto cuando el usuario mencione el
            número de un albarán concreto
        total_minimo: Filtrar albaranes con importe total igual o superior
        total_maximo: Filtrar albaranes con importe total igual o inferior
        facturado: Filtrar por si el albarán ya ha sido facturado o no
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas.
        orden: Orden de los resultados — uno de: fecha_asc, fecha_desc, total_asc,
            total_desc, codigo_asc, codigo_desc. Por defecto "fecha_desc" (los más
            recientes primero).
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba.
            Si el campo no es válido, la tool falla con la lista de campos válidos.

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    _aplicar_periodo(filtro, "fecha", periodo, fecha_desde, fecha_hasta)
    if codigo:
        filtro.append(["codigo", "~", codigo])
    if total_minimo is not None:
        filtro.append(["total", ">=", total_minimo])
    if total_maximo is not None:
        filtro.append(["total", "<=", total_maximo])
    if facturado is not None:
        filtro.append(["facturado", "=", facturado])
    filtro.extend(await clausulas_de_filtro_dinamico("ventas/albaran", filtro_extra))
    q = build_query(filtro or None, orden=_resolver_orden_documento_venta(
        orden), pagina=pagina, limite=limite)
    return await api_get_pagina("/ventas/albaran", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_albaran(albaran_id: str) -> dict:
    """
    Obtiene un albarán por su ID.

    Args:
        albaran_id: ID del albarán
    """
    return await api_get_one(f"/ventas/albaran/{albaran_id}")


# ── Facturas ──────────────────────────────────────────────────────────────


@mcp.tool()
async def buscar_factura(
    pagina: int = 1, limite: int = 100, cliente_id: str | None = None,
    fecha_desde: str | None = None, fecha_hasta: str | None = None, periodo: str | None = None,
    codigo: str | None = None, total_minimo: float | None = None,
    total_maximo: float | None = None, orden: str | None = None,
    filtro_extra: dict[str, str] | None = None,
) -> dict:
    """
    Busca facturas de venta. Para preguntas agregadas por periodo ("total facturado
    en 2025"), usa fecha_desde/fecha_hasta o periodo para filtrar en el servidor en
    vez de traer todo el histórico.

    Args:
        pagina: Número de página
        limite: Resultados por página (máximo 100)
        cliente_id: Filtrar por ID de cliente
        fecha_desde: Filtrar desde esta fecha, inclusive (formato YYYY-MM-DD)
        fecha_hasta: Filtrar hasta esta fecha, inclusive (formato YYYY-MM-DD)
        codigo: Filtrar por número/código de factura (coincidencia parcial, p. ej.
            "00123" encuentra "F2026-00123") — usa esto cuando el usuario mencione el
            número de una factura concreta
        total_minimo: Filtrar facturas con importe total igual o superior
        total_maximo: Filtrar facturas con importe total igual o inferior
        periodo: Atajo de fecha relativo a hoy en vez de fecha_desde/fecha_hasta —
            uno de: hoy, ayer, mañana, esta_semana, semana_anterior, semana_siguiente,
            este_mes, mes_anterior, mes_siguiente, este_año, año_anterior, año_siguiente.
            Se ignora si ya pasas fecha_desde o fecha_hasta explícitas.
        orden: Orden de los resultados — uno de: fecha_asc, fecha_desc, total_asc,
            total_desc, codigo_asc, codigo_desc. Por defecto "fecha_desc" (las más
            recientes primero).
        filtro_extra: Filtro EXACTO por cualquier otro campo que no esté arriba
            (p. ej. {"id_fiscal": "..."} para el CIF/NIF del cliente). Si el campo
            no es válido, la tool falla con la lista de campos válidos.

    Returns:
        {"resultados": [...], "pagina": N, "limite": N, "total": N|None,
        "hay_mas_resultados": bool}. "total" solo viene relleno en la página 1;
        usa "hay_mas_resultados" para saber si conviene pedir la siguiente página.
    """
    filtro = []
    if cliente_id:
        filtro.append(["cliente_id", "=", cliente_id])
    _aplicar_periodo(filtro, "fecha", periodo, fecha_desde, fecha_hasta)
    if codigo:
        filtro.append(["codigo", "~", codigo])
    if total_minimo is not None:
        filtro.append(["total", ">=", total_minimo])
    if total_maximo is not None:
        filtro.append(["total", "<=", total_maximo])
    filtro.extend(await clausulas_de_filtro_dinamico("ventas/factura", filtro_extra))
    q = build_query(filtro or None, orden=_resolver_orden_documento_venta(
        orden), pagina=pagina, limite=limite)
    return await api_get_pagina("/ventas/factura", params={"q": q}, pagina=pagina, limite=limite)


@mcp.tool()
async def obtener_factura(factura_id: str) -> dict:
    """
    Obtiene una factura por su ID.

    Args:
        factura_id: ID de la factura
    """
    return await api_get_one(f"/ventas/factura/{factura_id}")


@mcp.tool()
async def crear_factura(empresa_id: str, cliente: ClienteVenta, lineas: list[LineaVenta]) -> dict:
    """
    Crea una factura de venta.

    Args:
        empresa_id: ID de la empresa
        cliente: Datos del cliente (mismos formatos que crear_presupuesto)
        lineas: Lista de líneas [{"articulo": {"articulo_id": "..."}, "cantidad": N}, ...].
            Para una línea sin artículo de catálogo, usa
            {"articulo": {"descripcion": "...", "pvp_unitario": N}, "cantidad": N}.
    """
    body: dict = {"empresa_id": empresa_id,
                  "cliente": cliente, "lineas": lineas}
    return await api_post("/ventas/factura", body=body)


@mcp.tool()
async def emitir_factura(factura_id: str) -> dict:
    """
    Emite una factura de venta.

    Args:
        factura_id: ID de la factura a emitir
    """
    return await api_patch(f"/ventas/factura/{factura_id}/emitir")
