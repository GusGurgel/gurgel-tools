from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from apps import chronometers, create_db_and_tables

main_path = Path(__file__).resolve().parents[1]

# Lista dicionário atuando como fonte da verdade dos apps instalados
projects = [
    {
        "name": "Chronometers",
        "description": "App to track time.",
        "version": "1.0",
        "path": "src/apps/chronometers/chronometers.html",
        "end_point": "/chronometers",
        "icon": "clock",
        "icon_color": "#ff00ff",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse(main_path / "src/apps/index/index.html")


# Endpoint para o index.html consumir e renderizar a lista
@app.get("/api/projects")
async def get_projects():
    return JSONResponse(content=projects)


@app.get("/css/pico.min.css")
async def css_pico():
    return FileResponse(main_path / "pico/css/pico.min.css")


# Gerador Dinâmico de Rotas para os HTMLs
for proj in projects:
    # Usamos uma função closure para capturar o path correto no escopo do loop
    def create_html_handler(file_path: str):
        async def handler():
            return FileResponse(main_path / file_path)

        return handler

    app.add_api_route(
        path=proj["end_point"],
        endpoint=create_html_handler(proj["path"]),
        methods=["GET"],
        include_in_schema=False,  # Oculta as rotas de UI do /docs (Swagger)
    )

# Inicialização dos Módulos (Backend REST das ferramentas)
chronometers(app)
