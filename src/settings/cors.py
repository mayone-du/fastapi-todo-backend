from sys import path

from fastapi.middleware.cors import CORSMiddleware

path.append('../')
from app.main import app

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)