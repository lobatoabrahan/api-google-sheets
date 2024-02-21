from fastapi import HTTPException, status, APIRouter, Form
from pydantic import BaseModel, Field
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date, timedelta
from typing import Dict, List
from typing import Union

class Producto(BaseModel):
    id: str = str(uuid4())
    categoria: str

class Manga(BaseModel):
    id: str = str(uuid4())
    nombre: str
    ancho: int
    fuelle: int
    espesor: int
    mezcla: List[str] = []
    cof: int

class Bolsa(BaseModel):
    id: str = str(uuid4())
    nombre: str
    id_bobina: str
    largo: int
    cantidad_por_paquete: int
    
class Trazabilidad(BaseModel):
    id_producto: str
    id_producto_proveniente: str
    


router = APIRouter()

# Open the Google Spreadsheet by its name
libro = connect_to_sheet("productos")
hoja_caracteristicas = libro.worksheet("caracteristicas")

@router.post("/crear_producto")
async def crear_producto(producto_json: dict):
    try:
        # Crear producto con formato específico
        producto_id = str(uuid4())
        productos = []

        # Obtener la última fila de la hoja de cálculo
        last_row = len(hoja_caracteristicas.get_all_values()) + 1

        # Actualizar la hoja de cálculo con los valores del producto
        for categoria, valor in producto_json.items():
            productos.append({"id": producto_id, "categoria": categoria, "valor": str(valor)})

        for producto in productos:
            row_data = [producto["id"], producto["categoria"], producto["valor"]]
            hoja_caracteristicas.update(f"A{last_row}", producto["id"])
            hoja_caracteristicas.update(f"B{last_row}", producto["categoria"])
            hoja_caracteristicas.update(f"C{last_row}", producto["valor"])
            last_row += 1

        return {"message": "Producto creado exitosamente"}
    except Exception as e:
        print(f"Error al crear producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))