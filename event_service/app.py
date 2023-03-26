from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def welcome(status_code = status.HTTP_200_OK):
    return "Welcome to event service!!" 