# materia_prima.py
from fastapi import HTTPException, status, APIRouter
from pydantic import BaseModel
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date, timedelta

class MateriaPrima(BaseModel):
    id: str = str(uuid4())
    codigo: str
    descripcion: str
    categoria: str
    cantidad_minima: int
    proveedor: str
    presentacion: str
    peso_presentacion: int
    stock: int
    fecha_creacion: datetime = datetime.now()
    fecha_actualizacion: datetime = datetime.now()
    usuario_creacion: str
    usuario_actualizacion: str
    
router = APIRouter()

# Open the Google Spreadsheet by its name
sheet = connect_to_sheet("materias_primas")

@router.get("/materias_primas")
async def get_materias_primas(limit: int = None):
    try:
        materias_primas = sheet.worksheet("productos").get_all_records()
        if limit is not None:
            materias_primas = materias_primas[:limit]
        return materias_primas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crear_materia_prima")
async def create_materia_prima(materia_prima: MateriaPrima):
    try:
        sheet.worksheet("productos").append_row([ materia_prima.id, materia_prima.codigo, materia_prima.descripcion, materia_prima.categoria, materia_prima.cantidad_minima, materia_prima.proveedor, materia_prima.presentacion, materia_prima.peso_presentacion, materia_prima.stock, materia_prima.fecha_creacion.isoformat(), materia_prima.fecha_actualizacion.isoformat(), materia_prima.usuario_creacion, materia_prima.usuario_actualizacion])
        return {"message": "Materia prima creada exitosamente", "materia_prima": materia_prima}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materia_prima/{id}")
async def get_materia_prima(id: str):
    materia_prima = sheet.worksheet("productos").get_all_records()
    for mp in materia_prima:
        if mp['id'] == id:
            return mp
    raise HTTPException(status_code=404, detail="Materia prima no encontrada")
        