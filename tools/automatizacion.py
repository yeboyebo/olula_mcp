from server import mcp
from client import api_get_many, api_post, api_patch


@mcp.tool()
async def programar_tarea_ia(
    nombre: str,
    ia_flujo_id: str,
    expresion_cron: str,
    activo: bool = True,
) -> dict:
    """
    Programa la ejecución periódica y automática (sin supervisión humana) de un
    flujo de trabajo de IA existente, según una expresión cron.

    Cualquier acción de escritura que el flujo intente durante una ejecución
    programada queda pendiente de confirmación humana — revisable desde el
    historial de la tarea o desde el propio chat.

    Args:
        nombre: Nombre descriptivo de la tarea (p.ej. "Revisión diaria de pedidos").
        ia_flujo_id: Id o nombre de un flujo de trabajo de IA ya existente
            (ver obtener_flujo_trabajo / la sección "Flujos de trabajo" del asistente).
        expresion_cron: Expresión cron de 5 campos (minuto hora día mes día_semana),
            p.ej. "0 8 * * *" para todos los días a las 8:00.
        activo: Si la tarea empieza activa nada más crearla (por defecto sí).
    """
    body = {
        "nombre": nombre,
        "ia_flujo_id": ia_flujo_id,
        "expresion_cron": expresion_cron,
        "activo": activo,
    }
    return await api_post("/comun/ia-tarea-programada", body=body)


@mcp.tool()
async def listar_tareas_programadas_ia() -> list[dict]:
    """
    Lista las tareas de IA programadas (nombre, expresión cron, flujo asociado,
    próxima ejecución, si está activa).
    """
    return await api_get_many("/comun/ia-tarea-programada")


@mcp.tool()
async def cambiar_estado_tarea_programada_ia(tarea_id: str, activo: bool) -> dict:
    """
    Activa o desactiva una tarea de IA programada existente, sin borrarla.

    Args:
        tarea_id: Id de la tarea programada (ver listar_tareas_programadas_ia).
        activo: True para activarla, False para pausarla.
    """
    return await api_patch(f"/comun/ia-tarea-programada/{tarea_id}", body={"activo": activo})
