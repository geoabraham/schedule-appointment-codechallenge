from fastapi import FastAPI

from .database import engine
from .routers import appointment, auth, user

app = FastAPI(title="Schedule Appointment")


app.include_router(appointment.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World!!"}
