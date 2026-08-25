"""
Tipos compartidos entre módulos de tools/ para los cuerpos de creación de
documentos de venta (presupuesto, pedido, factura) y afines.

Se definen como TypedDict (en vez de `dict` a secas) para que fastmcp genere
un JSON schema preciso de cada tool: así el LLM que llama a la tool ve la
forma real que espera el backend (p. ej. que el id de artículo va anidado
bajo "articulo") en lugar de tener que adivinarla a partir de la docstring.
"""
from typing import NotRequired, TypedDict


class ArticuloCatalogo(TypedDict):
    """Referencia a un artículo ya existente en el catálogo."""
    articulo_id: str


class ArticuloLibre(TypedDict):
    """Línea sin artículo de catálogo: descripción y precio a mano."""
    descripcion: str
    pvp_unitario: float


class LineaVenta(TypedDict):
    """
    Línea tal y como la espera el servidor en presupuesto/pedido/factura:
    el bloque "articulo" es excluyente (id de catálogo o descripción con
    precio) y "cantidad" va fuera de él.
    """
    articulo: ArticuloCatalogo | ArticuloLibre
    cantidad: float


class ClientePorEmail(TypedDict):
    """Busca un cliente ya registrado por su email."""
    email: str


class ClienteRegistrado(TypedDict):
    """Cliente ya registrado, referenciado por ID."""
    cliente_id: str
    direccion_id: NotRequired[str]


class ClienteNoRegistrado(TypedDict):
    """Cliente sin ficha previa: se crea al vuelo con estos datos."""
    nombre: str
    id_fiscal: str


ClienteVenta = ClientePorEmail | ClienteRegistrado | ClienteNoRegistrado
