from fastapi import HTTPException, status, APIRouter
from pydantic import BaseModel, Field
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date, timedelta
from typing import Dict, List

class Bobina(BaseModel):
    id: str = str(uuid4())
    nombre: str
    categoria: str
    ancho: int
    espesor: int
    mezcla: List[str] = []
    cof: int
    fecha_creacion: datetime = datetime.now()
    fecha_actualizacion: datetime = datetime.now()
    usuario_creacion: str
    usuario_actualizacion: str
    
class Tubular (Bobina):
    fuelle: int
    
class Termoencogible (Bobina):
    md:int
    td:int
    
class Bolsa (BaseModel):
    id: str = str(uuid4())
    id_bobina: str
    nombre: str
    largo: int
    cantidad_por_paquete: int

router = APIRouter()

# Open the Google Spreadsheet by its name
sheet = connect_to_sheet("productos")

@router.get("/producto/{categoria}")
async def get_bobinas(categoria: str, limit: int = None):
    try:
        productos = sheet.worksheet(categoria).get_all_records()
        if limit is not None:
            productos = productos[:limit]
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/producto/{categoria}/{id}")
async def get_producto(categoria: str, id: str):
    try:
        productos = sheet.worksheet(categoria).get_all_records()
        for producto in productos:
            if producto['id'] == id:
                return producto
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/producto/{categoria}")
async def add_producto(categoria: str, producto: Dict[str, str]):
    try:
        hoja = sheet.worksheet(categoria)
        titulos = hoja.row_values(1)  # Asume que los títulos están en la primera fila
        fila = [producto.get(titulo, '') for titulo in titulos]
        hoja.append_row(fila)
        return {"message": "Producto agregado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))