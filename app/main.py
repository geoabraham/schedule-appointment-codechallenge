from time import sleep

import psycopg2
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor

from . import models
from .database import engine
from .routers import appointment, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="appointment-scheduler",
            user="gabraham",
            password="#pSQL_00!",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        break
    except Exception as error:
        print("Database connection failed")
        print("error: ", error)
        print("Reconnecting in 30 seconds...")
        sleep(30)

app.include_router(appointment.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Hello World!!"}
