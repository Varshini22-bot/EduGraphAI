from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.auth_routes import router as auth_router
from api.graph_routes import router as graph_router

from database.database import engine, Base
from database import models


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Knowledge Graph Learning Assistant"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(router)

app.include_router(auth_router)

app.include_router(graph_router)


@app.get("/")
def root():

    return {
        "message":
        "Knowledge Graph Learning Assistant Backend Running"
    }