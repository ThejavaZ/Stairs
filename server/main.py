from fastapi import FastAPI
import uvicorn
from app.models.user import User

app = FastAPI(
    title="My api",
    description="",
    version="0.0.1",
    docs_url="/docs" if True else None,
    redoc_url="/redoc" if True else None,
    openapi_url="/openapi.json" if True else None,
)

PORT = 8000

users = []

user = {
    "id": int,
    "name" : str,
    "email" : str
}

@app.get("/api/")
async def get_home():
    return { "message": "Hello world" }

@app.get("/api/users")
async def get_users():
    return { "users" : { "data": [user for user in users if user["id"] == True] } }

@app.get("/api/users/{user_id}/show")
async def get_user(user_id:int):
    return {"Message": "Usuario obtenido correctamente!", "data": ""}

@app.post("/api/users/store")
async def post_user(user: User):
    return {"message":"Usuario creado satisfactoria mente", "user": {"data": {"id" : user.id, "name": user.name}}}

@app.patch("/api/users/{user_id}/change_password")
async def patch_user(user_id:int):
    return {}

@app.put("/api/users/{user_id}/update")
async def put_user(user_id:int):
    return {"message": "Usuario actualizado satisfactoriamente", "data" : {}}

@app.delete("/api/users/{user_id}/destroy")
async def delete_user(user_id: int):
    return {}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=PORT, reload=True)