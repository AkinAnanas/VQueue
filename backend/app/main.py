from fastapi import FastAPI
from fastapi import Path
from utils import format_response, generate_code

app = FastAPI()

@app.get("/")
async def root():
    return format_response(200, "ServiceProviders: ")

"""
User-facing
"""
@app.post("/queue/join/{code}")
async def join_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return format_response(200, code)

@app.get("/queue/status/{code}/{party_id}")
async def status_queue(party_id: int, code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return format_response(200, code)

@app.delete("/queue/{code}/{party_id}")
async def delete_queue(party_id: int, code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return format_response(200, code)


"""
ServiceProvider-facing
"""
@app.post("/queue/create")
async def create_queue():
    code = generate_code() # 6-digit alpha-numeric code associated with queue
    return format_response(200, code)

@app.patch("/queue/{code}/close")
async def close_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    # Close the queue
    return 204

@app.post("/queue/{code}/dispatch")
async def dispatch_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    # Dispatch the current block in the queue
    return 204

"""
Dev-facing
"""
@app.get("/dashboard/stats")
async def dashboard_stats():
    return format_response(200, {})
