from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from .sheets import connect_to_sheet
from datetime import datetime

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
        worksheet = sheet.worksheet("registro_extrusion")
        last_row = len(worksheet.get_all_values()) + 1

        # Convertir la fecha y la hora a objetos de fecha y hora de Python
        fecha = datetime.strptime(fecha, "%d-%m-%Y").date()
        hora = datetime.strptime(hora, "%H:%M").time()

        worksheet.update(f"C{last_row}", fecha)
        worksheet.update(f"D{last_row}", turno)
        worksheet.update(f"E{last_row}", operador)
        worksheet.update(f"F{last_row}", extrusora)
        worksheet.update(f"G{last_row}", lote)
        worksheet.update(f"J{last_row}", numero_bobina)
        worksheet.update(f"K{last_row}", hora)
        worksheet.update(f"L{last_row}", kg)
        worksheet.update(f"M{last_row}", empates)
        worksheet.update(f"N{last_row}", estatus)
        
        return {"message": "Materia prima creada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
router.get("/maquina/estatus")
async def get_maquina_estatus():
    try:
        worksheet = sheet.worksheet("paradas_maquina")
        data = worksheet.get("I1:J4")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
router.patch("/maquina/estatus/{maquina}")
async def update_maquina_estatus(maquina: str):
    try:
        worksheet = sheet.worksheet("paradas_maquina")
        data = worksheet.get("I1:J4")
        for index, row in enumerate(data):
            if row[0] == maquina:
                if row[1] == "Activo":
                    row[1] = "Parada"
                elif row[1] == "Parada":
                    row[1] = "Activo"
                else:
                    return {"message": "Estado desconocido"}
                worksheet.update_cell(index+1, 10, row[1])
                return {"message": "Maquina actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
router.post("/maquina/parada")
async def crear_parada_maquina(
    maquina: str = Form(...),
    fecha_hora: str = Form(...),
    motivo: str = Form(...)
):
    try:
        worksheet = sheet.worksheet("paradas_maquina")
        all_values = worksheet.get_all_values()
        
        # Buscar el último registro para la máquina en cuestión
        last_row = len(all_values)
        ultima_parada = None

        for row in reversed(all_values[1:]):
            if row[0] == maquina:
                ultima_parada = row
                break

        # Convertir la fecha y la hora a objetos de fecha y hora de Python
        fecha_hora_split = fecha_hora.split(" ")  # Separar fecha y hora
        fecha = datetime.strptime(fecha_hora_split[0], "%d/%m/%Y").date()
        hora = datetime.strptime(fecha_hora_split[1], "%I:%M %p").time()
        fecha_hora_real = fecha + " " + hora

        if ultima_parada and ultima_parada[2]:  # Verificar si hay una fecha final en el último registro
            # Crear un nuevo registro
            last_row += 1
            worksheet.update(f"A{last_row}", maquina)
            worksheet.update(f"B{last_row}", fecha_hora_real)
            worksheet.update(f"D{last_row}", motivo)
        elif ultima_parada:
            # Actualizar la fecha final en el último registro
            last_row = worksheet.find(ultima_parada[2]).row  # Encontrar la fila del último registro
            worksheet.update(f"C{last_row}", fecha_hora_real)  # Actualizar la hora en lugar de la fecha final

        return {"message": "Parada de maquina creada o actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

