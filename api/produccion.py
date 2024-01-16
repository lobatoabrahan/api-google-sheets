from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from .sheets import connect_to_sheet
from datetime import date, time, datetime

class Registro_Extrusion(BaseModel):
    fecha: str
    turno: str
    operador: str
    extrusora: int
    lote: int
    numero_bobina: int
    hora: str
    kg: float
    empates: int
    estatus: str

router = APIRouter()

sheet = connect_to_sheet("registro_produccion")

@router.post("/crear_registro_extrusion")
async def crear_registro_extrusion(
    fecha: str = Form(...),
    turno: str = Form(...),
    operador: str = Form(...),
    extrusora: str = Form(...),
    lote: str = Form(...),
    numero_bobina: str = Form(...),
    hora: str = Form(...),
    kg: float = Form(...),
    empates: int = Form(...),
    estatus: str = Form(...)
):
    try:
        worksheet = sheet.worksheet("productos")
        last_row = len(worksheet.get_all_values()) + 1
        worksheet.update(f"C{last_row}", fecha.strftime("%d/%m/%Y"))
        worksheet.update(f"D{last_row}", turno)
        worksheet.update(f"E{last_row}", operador)
        worksheet.update(f"F{last_row}", extrusora)
        worksheet.update(f"G{last_row}", lote)
        worksheet.update(f"J{last_row}", numero_bobina)
        worksheet.update(f"K{last_row}", hora.strftime("%H:%M"))
        worksheet.update(f"L{last_row}", kg)
        worksheet.update(f"M{last_row}", empates)
        worksheet.update(f"N{last_row}", estatus)
        
        return {"message": "Materia prima creada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))