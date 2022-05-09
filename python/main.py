import os
import logging
import pathlib
import json
import sqlite3
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

sqlite_path = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve() / "db" / "mercari.sqlite3")

def get_items_json():
    with open('items.json', 'r', encoding='utf-8') as f:
        items_json = json.load(f)
    return items_json

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    logger.info(f"Receive item: {name}")
    items_json = get_items_json()
    items_json['items'].append({'name': name, 'category': category})
    with open('items.json', 'w', encoding='utf-8') as f:
        json.dump(items_json, f, indent=4)
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    return get_items_json()

@app.get("/search")
def search_items(keyword: str):
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, category FROM items WHERE name LIKE '%{keyword}%'")
    sql_res = cursor.fetchall()
    conn.close()
    result_dict = {}
    result_dict['items'] = [{'name': name, 'category': category} for name, category in sql_res]
    return result_dict

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
