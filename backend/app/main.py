from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import User, StudentTask, Class
import socketio

origins = [
    "http://localhost:3000",
]

Base.metadata.create_all(bind=engine)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
fastapi_app = FastAPI()

_socket_app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
asgi_app = CORSMiddleware(
    _socket_app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)