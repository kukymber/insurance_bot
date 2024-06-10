import uvicorn
from fastapi import FastAPI
from src.api.router import user_router, server

app = FastAPI()

app.include_router(user_router, prefix='/users')
app.include_router(server)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
