from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import appointment, auth, user

app = FastAPI(title="Schedule Appointment")

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appointment.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World!!"}
