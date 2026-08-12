from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    return FileResponse('apps/lucide.html')

@app.get("/css/pico.min.css")
async def css_pico():
    return FileResponse('pico/css/pico.min.css')
