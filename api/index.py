import os
from fastapi import FastAPI, Request
from sys import version as python_formatted_version
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
import redis

app = FastAPI()

KV_USERNAME = os.environ.get('KV_USERNAME')
KV_PASS = os.environ.get('KV_PASS')
KV_HOST = os.environ.get('KV_HOST')
KV_PORT = os.environ.get('KV_PORT')

r = redis.Redis(
    host=KV_HOST,
    port=KV_PORT,
    username=KV_USERNAME,
    password=KV_PASS,
    ssl=True,
    decode_responses=True 
)

@app.get("/")
async def root():
    return {"GMT+11 time": format(datetime.utcnow()+timedelta(hours=11))}

@app.get("/r")   # GET
async def r_add(request: Request):
    time_str = format(datetime.utcnow()+timedelta(hours=11))+" GMT+11"
    params = request.query_params
    
    if 'add' in params:
        try:
            r.lpush('list_val', time_str+' (GET) '+str(params['add']))
            r.ltrim('list_val', 0, 37)
        except redis.exceptions.ConnectionError:
            return {"error": "Redis Connection failed. Check Vercel KV linking."}

    try:
        values = r.lrange('list_val', 0, 38)
    except redis.exceptions.ConnectionError:
        return {"error": "Redis Connection failed"}

    safe_values = values if values is not None else []
    return {"redis_values": safe_values} 

@app.post("/r")   # POST
async def r_post_add(request: Request):
    time_str = format(datetime.utcnow()+timedelta(hours=11))+" GMT+11"
    
    if 'add' in request.headers:
        add_value = request.headers.get('add')
        try:
            r.lpush('list_val', time_str+' (POST) '+str(add_value))
            r.ltrim('list_val', 0, 37)
        except redis.exceptions.ConnectionError:
            return {"error": "Redis Connection failed"}
            
    try:
        values = r.lrange('list_val', 0, 38)
    except redis.exceptions.ConnectionError:
        return {"error": "Redis Connection failed"}

    safe_values = values if values is not None else []
    return {"redis_values": safe_values }


@app.get("/html", response_class=HTMLResponse)
async def root_html():
    return """
    <html>
        <head><title>Some HTML in here</title> </head>
        <body><h1>Look me! HTMLResponse!</h1></body>
    </html> """+'@python '+str(python_formatted_version)
