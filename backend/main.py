from fastapi import FastAPI
from database import get_connection

app = FastAPI()

@app.get("/api/despesas")
def listar_despesas():

    return despesas
