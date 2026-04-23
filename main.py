import os
from contextlib import asynccontextmanager
from typing import TypedDict

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
import uvicorn

load_dotenv()

host = 'http://localhost:5000'

# 1. Creamos la instancia de FastMCP
mcp = FastMCP("olula", json_response=True, host="0.0.0.0")

# 2. Definimos una herramienta simple para testear


class ClienteComandoCrearPresupuesto(TypedDict):
    email: str


class LineaComandoCrearPresupuesto(TypedDict):
    articulo_id: str
    cantidad: float


class ComandoCrearPresupuesto(TypedDict):
    empresa_id: str
    cliente: ClienteComandoCrearPresupuesto
    lineas: list[LineaComandoCrearPresupuesto]


class ParamArticuloCrearPresupuesto(TypedDict):
    sku: str
    cantidad: float


@mcp.tool()
def buscar_cliente(nombre: str) -> list[dict]:
    """
    Busca clientes por nombre

    Devuelve una lista de clientes en formato JSON
    """
    import json
    q = json.dumps({
        "filtro": [["nombre", "~", nombre]],
        "orden": ["nombre", "DESC"],
        "paginacion": {"pagina": 1, "limite": 100}
    }, ensure_ascii=False, separators=(',', ':'))
    api_key = os.getenv("API_KEY_EGICAR")
    response = requests.get(
        f"{host}/ventas/cliente",
        params={"q": q},
        headers={"Authorization": f"X-Api-Key {api_key}"}
    )
    response.raise_for_status()
    return response.json()["datos"]


@mcp.tool()
def crear_presupuesto_por_email(email: str, articulos: list[ParamArticuloCrearPresupuesto]) -> dict:
    """
    Crea un presupuesto de venta para un cliente identificado por email
    """
    api_key = os.getenv("API_KEY_EGICAR")
    comando: ComandoCrearPresupuesto = {
        "empresa_id": "1",
        "cliente": {"email": email},
        "lineas": [
            {
                "articulo_id": a["sku"],
                "cantidad": a["cantidad"]
            }
            for a in articulos
        ]
    }
    response = requests.post(
        f"{host}/ventas/presupuesto",
        json=comando,
        headers={"Authorization": f"X-Api-Key {api_key}"}
    )
    response.raise_for_status()
    return response.json()


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# 3. Montamos el transporte streamable HTTP (esto inicializa el session_manager)
streamable_app = mcp.streamable_http_app()  # type: ignore[attr-defined]


# 4. Configuramos FastAPI con lifespan para inicializar el task group
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():  # type: ignore[attr-defined]
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Transporte moderno (streamable HTTP) en /mcp
app.mount("/", streamable_app)


# Transporte legacy SSE en /sse y /messages
app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# .venv/bin/python main.py
