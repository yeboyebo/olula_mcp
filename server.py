from mcp.server.fastmcp import FastMCP

mcp = FastMCP("olula", host="0.0.0.0", port=8000)

import tools.ventas  # noqa: F401
import tools.crm  # noqa: F401
import tools.almacen  # noqa: F401
import tools.tpv  # noqa: F401
import tools.tesoreria  # noqa: F401
import tools.compras  # noqa: F401
import tools.comun  # noqa: F401
import tools.predicciones  # noqa: F401
import tools.documental  # noqa: F401