# auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date

class Usuario(BaseModel):
    id: str = str(uuid4())
    usuario: str
    contraseña: str
    nombre: str
    apellido: str
    nacimiento: date
    id_rol: int
    empresa: str
    fecha_creacion: datetime = datetime.now()
    fecha_actualizacion: datetime = datetime.now()
    

router = APIRouter()

# Connect to the Google Spreadsheet
sheet = connect_to_sheet("auth")

@router.post("/crear_usuario")
async def create_user(user: Usuario):
    # Append a new record to the Google Spreadsheet
    sheet.worksheet("usuario").append_row([user.id, user.usuario, user.contraseña, user.nombre, user.apellido, user.nacimiento, user.id_rol, user.empresa, user.fecha_creacion, user.fecha_actualizacion])
    return {"message": "User created successfully"}