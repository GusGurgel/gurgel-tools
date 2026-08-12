from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

main_path = Path(__file__).resolve().parents[1]

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse(main_path / "src/apps/index/index.html")


@app.get("/css/pico.min.css")
async def css_pico():
    return FileResponse("./pico/css/pico.min.css")
