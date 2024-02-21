import uvicorn
from fastapi import FastAPI
from src.api.router import user_router

app = FastAPI()

app.include_router(user_router, prefix='/users')

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
