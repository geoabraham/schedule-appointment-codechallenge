from time import sleep

import psycopg2
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor

from . import models
from .database import engine
from .routers import appointment, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Schedule Appointment")


app.include_router(appointment.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World!!"}
