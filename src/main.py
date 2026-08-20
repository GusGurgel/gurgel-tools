from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from apps import chronometers, create_db_and_tables, goals, prompt_templates, snippets

main_path = Path(__file__).resolve().parents[1]

projects = [
    {
        "name": "Chronometers",
        "description": "App to track time.",
        "version": "1.0",
        "path": "src/apps/chronometers/chronometers.html",
        "end_point": "/chronometers",
        "icon": "alarm-clock",
        "icon_color": "#c56cff",
    },
    {
        "name": "Snippets",
        "description": "Store, organize, and quickly copy chunks of information.",
        "version": "1.0",
        "path": "src/apps/snippets/snippets.html",
        "end_point": "/snippets",
        "icon": "scissors",
        "icon_color": "#10b981",
    },
    {
        "name": "Prompt Templates",
        "description": "Create, manage, and use text templates with dynamic variables.",
        "version": "1.0",
        "path": "src/apps/prompt_templates/prompt_templates.html",
        "end_point": "/prompt-templates",
        "icon": "library",
        "icon_color": "#3b82f6",
    },
    {
        "name": "Goals",
        "description": "Track integer-based objectives by adding increments over time.",
        "version": "1.0",
        "path": "src/apps/goals/goals.html",
        "end_point": "/goals",
        "icon": "target",
        "icon_color": "#ef4444",
    },
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


@app.get("/api/projects")
async def get_projects():
    return JSONResponse(content=projects)


@app.get("/css/pico.min.css")
async def css_pico():
    return FileResponse(main_path / "pico/css/pico.min.css")


for proj in projects:

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

chronometers(app)
snippets(app)
prompt_templates(app)
goals(app)
