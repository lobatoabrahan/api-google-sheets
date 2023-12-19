# auth.py
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from pydantic import BaseModel
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
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

@router.post("/crear_usuario")
async def create_user(user: Usuario):
    # Store the password without hashing
    sheet.worksheet("usuario").append_row([user.id, user.usuario, user.contraseña, user.nombre, user.apellido, user.nacimiento.isoformat(), user.id_rol, user.empresa, user.fecha_creacion.isoformat(), user.fecha_actualizacion.isoformat()])
    return {"message": "User created successfully"}

@router.post("/login")
async def login(user: Login):
    u = find_user(user.usuario)
    if u and user.contraseña == u['contraseña']:
        expiry = datetime.utcnow() + timedelta(days=7)
        return {"token": u['id_usuario'], "expiry": expiry.isoformat()}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    u = find_user(token)
    if u and datetime.fromisoformat(u['expiry']) > datetime.utcnow():
        return u
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return current_user