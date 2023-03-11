from fastapi import FastAPI
import json
import uvicorn
import subprocess

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/mhapi/{idr}")
async def get_database_reference(idr: str):
    """Makes test request to database."""
    # Open database in haupt.json
    with open("haupt.json", "r") as f:
        data = json.load(f)
    # Get the data from the database
    try:
        data = data[idr]
    except KeyError:
        return {
            "error": [404, "No data found"]
        }
    return {
        "OK": [200, data],
    }


@app.get("/mhapi/controls/start/{idr}")
async def start_bot(idr: str, basic_key: str = None):
    """Starts the bot."""
    # Open database in haupt.json
    with open("haupt.json", "r") as f:
        data = json.load(f)
    
    with open("auth.json", "r") as f:
        auth = json.load(f)
    
    with open("verlangsamung.json", "r") as f:
        verlangsamung = json.load(f)
    # Get the data from the database
    try:
        data = data[idr]
        verlangsamung = verlangsamung[idr]
    except KeyError:
        return {
            "error": [404, "No data found"]
        }
    
    if verlangsamung["verlangsamt"]:
        return {
            "error": [429, f"Too many requests. Try again at {verlangsamung['vbis']}",  verlangsamung['vbis']]
        }
    
    if data['banned']:
        return {
            "error": [403, "You are banned"]
        }
    
    try:
        auth_keys = auth[idr]
    except KeyError:
        return {
            "error": [403, "API auth isn't enabled"]
        }
    
    if basic_key is None:
        return {
            "error": [401, "Unauthorized"]
        }
    
    if basic_key != auth_keys["basic"]:
        return {
            "error": [401, "Auth key doesn't match"]
        }
    
    if not data['installed'] or not data['activated']:
        return {
            "error": [400, "No container"]
        }

    import utilities.MHdocker as dckr
    dckr.start(idr)

    return {
        "OK": [200, "Started"]
    }


@app.get("/mhapi/controls/stop/{idr}")
async def stop_bot(idr: str, basic_key: str = None):
    """Stops the bot."""
    # Open database in haupt.json
    with open("haupt.json", "r") as f:
        data = json.load(f)
    
    with open("auth.json", "r") as f:
        auth = json.load(f)
    
    with open("verlangsamung.json", "r") as f:
        verlangsamung = json.load(f)
    # Get the data from the database
    try:
        data = data[idr]
        verlangsamung = verlangsamung[idr]
    except KeyError:
        return {
            "error": [404, "No data found"]
        }
    
    if verlangsamung["verlangsamt"]:
        return {
            "error": [429, f"Too many requests. Try again at {verlangsamung['vbis']}",  verlangsamung['vbis']]
        }
    
    if data['banned']:
        return {
            "error": [403, "You are banned"]
        }
    
    try:
        auth_keys = auth[idr]
    except KeyError:
        return {
            "error": [403, "API auth isn't enabled"]
        }
    
    if basic_key is None:
        return {
            "error": [401, "Unauthorized"]
        }
    
    if basic_key != auth_keys["basic"]:
        return {
            "error": [401, "Auth key doesn't match"]
        }
    
    if not data['installed'] or not data['activated']:
        return {
            "error": [400, "No container"]
        }
    
    import utilities.MHdocker as dckr
    dckr.stop(idr)

    return {
        "OK": [200, "Stopped"]
    }


@app.get("/mhapi/controls/restart/{idr}")
async def restart_bot(idr: str, basic_key: str = None):
    """Restarts the bot."""
    # Open database in haupt.json
    with open("haupt.json", "r") as f:
        data = json.load(f)
    
    with open("auth.json", "r") as f:
        auth = json.load(f)
    
    with open("verlangsamung.json", "r") as f:
        verlangsamung = json.load(f)
    # Get the data from the database
    try:
        data = data[idr]
        verlangsamung = verlangsamung[idr]
    except KeyError:
        return {
            "error": [404, "No data found"]
        }
    
    if verlangsamung["verlangsamt"]:
        return {
            "error": [429, f"Too many requests. Try again at {verlangsamung['vbis']}",  verlangsamung['vbis']]
        }
    
    if data['banned']:
        return {
            "error": [403, "You are banned"]
        }
    
    try:
        auth_keys = auth[idr]
    except KeyError:
        return {
            "error": [403, "API auth isn't enabled"]
        }
    
    if basic_key is None:
        return {
            "error": [401, "Unauthorized"]
        }
    
    if basic_key != auth_keys["basic"]:
        return {
            "error": [401, "Auth key doesn't match"]
        }
    
    if not data['installed'] or not data['activated']:
        return {
            "error": [400, "No container"]
        }
    
    import utilities.MHdocker as dckr
    dckr.restart(idr)

    return {
        "OK": [200, "Restarted"]
    }


@app.get('/mhapi/commons/bot/restart')
async def botstart(key: str = None):
    if key != 'incorrectpasswordoops':
        return {"error": [401, "Auth key doesn't match"]}
    
    subprocess.run(['sudo', 'systemctl', 'restart', 'miyahostbot'])

    return {'OK': [200, 'Service restarted']}


@app.get('/mhapi/commons/bot/start')
async def botstart(key: str = None):
    if key != 'incorrectpasswordoops':
        return {"error": [401, "Auth key doesn't match"]}
    
    subprocess.run(['sudo', 'systemctl', 'start', 'miyahostbot'])

    return {'OK': [200, 'Service started']}


@app.get('/mhapi/commons/bot/stop')
async def botstop(key: str = None):
    if key != 'incorrectpasswordoops':
        return {"error": [401, "Auth key doesn't match"]}
    
    subprocess.run(['sudo', 'systemctl', 'stop', 'miyahostbot'])

    return {'OK': [200, 'Service stopped']}


if __name__ == "__main__":
    uvicorn.run("api:app")
