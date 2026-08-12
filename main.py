from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
async def index():
    # Returns the HTML file directly to the browser
    return FileResponse('apps/hello_world.html')

@app.get("/css/pico.min.css")
async def css_pico():
    # Returns the HTML file directly to the browser
    return FileResponse('pico/css/pico.min.css')
