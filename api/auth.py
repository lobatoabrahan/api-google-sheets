# auth.py
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from pydantic import BaseModel
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date, timedelta
from fastapi.security import OAuth2PasswordBearer

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
    
class Login(BaseModel):
    usuario: str
    contraseña: str

router = APIRouter()

# Connect to the Google Spreadsheet
sheet = connect_to_sheet("auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def find_user(username: str):
    users = sheet.worksheet("usuario").get_all_records()
    for u in users:
        if u['usuario'] == username:
            return u
    return None

def find_user_by_id(id: str):
    users = sheet.worksheet("usuario").get_all_records()
    for u in users:
        if u['id_usuario'] == id:
            return u
    return None

@router.post("/crear_usuario")
async def create_user(user: Usuario):
    # Store the password without hashing
    sheet.worksheet("usuario").append_row([user.id, user.usuario, user.contraseña, user.nombre, user.apellido, user.nacimiento.isoformat(), user.id_rol, user.empresa, user.fecha_creacion.isoformat(), user.fecha_actualizacion.isoformat()])
    return {"message": "User created successfully"}

@router.post("/login")
async def login(user: Login):
    try:
        u = find_user(user.usuario)
        if u and user.contraseña == u['contraseña']:
            expiry = datetime.utcnow() + timedelta(days=7)
            return {"token": u['id_usuario'], "expiry": expiry.isoformat(), "role":u['id_rol']}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        u = find_user_by_id(token)
        if u:
            return u
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    user = find_user_by_id(current_user)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )
    
@router.get("/users")
async def read_users():
    try:
        users = sheet.worksheet("usuario").get_all_records()
        # No incluir las contraseñas en la respuesta
        for user in users:
            del user['password']
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
