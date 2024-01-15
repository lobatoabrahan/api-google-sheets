from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .sheets import connect_to_sheet
from datetime import date, time, datetime

class Registro_Extrusion(BaseModel):
    fecha: date
    turno: str
    operador: str
    extrusora: int
    lote: int
    numero_bobina: int
    hora: time
    kg: float
    empates: int
    estatus: str

router = APIRouter()

sheet = connect_to_sheet("registro_produccion")

@router.post("/crear_registro_extrusion")
async def crear_registro_extrusion(registro_extrusion: Registro_Extrusion):
    try:
        worksheet = sheet.worksheet("productos")
        last_row = len(worksheet.get_all_values()) + 1
        worksheet.update(f"C{last_row}", registro_extrusion.fecha.strftime("%d/%m/%Y"))
        worksheet.update(f"D{last_row}", registro_extrusion.turno)
        worksheet.update(f"E{last_row}", registro_extrusion.operador)
        worksheet.update(f"F{last_row}", registro_extrusion.extrusora)
        worksheet.update(f"G{last_row}", registro_extrusion.lote)
        worksheet.update(f"J{last_row}", registro_extrusion.numero_bobina)
        worksheet.update(f"K{last_row}", registro_extrusion.hora.strftime("%H:%M"))
        worksheet.update(f"L{last_row}", registro_extrusion.kg)
        worksheet.update(f"M{last_row}", registro_extrusion.empates)
        worksheet.update(f"N{last_row}", registro_extrusion.estatus)
        
        return {"message": "Materia prima creada exitosamente", "registro_extrusion": registro_extrusion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))