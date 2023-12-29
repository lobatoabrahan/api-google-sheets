from fastapi import HTTPException, status, APIRouter
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
sheet = connect_to_sheet("productos")

def find_trazabilidad_by_id(id: str, id_type: str):
    hoja = sheet.worksheet("trazabilidad")
    filas = hoja.get_all_values()
    titulos = filas[0]
    id_index = titulos.index(id_type)

    trazabilidad = []
    for fila in filas[1:]:
        if fila[id_index] == id:
            trazabilidad.append(dict(zip(titulos, fila)))

    return trazabilidad

@router.get("/productos")
async def get_productos(limit: int = None):
    try:
        productos = sheet.worksheet("productos").get_all_records()
        if limit is not None:
            productos = productos[:limit]
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/productos/{categoria}")
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
    
@router.post("/producto")
async def add_producto(producto: Union[Manga, Bolsa]):
    try:
        hoja = sheet.worksheet(producto.categoria)
        producto_dict = producto.dict()
        titulos = hoja.row_values(1)  # Asume que los títulos están en la primera fila

        # Añadir títulos que no existen
        for titulo in producto_dict.keys():
            if titulo not in titulos:
                hoja.append_row([titulo])

        # Actualizar los títulos después de añadir nuevos
        titulos = hoja.row_values(1)

        fila = [producto_dict.get(titulo, '') for titulo in titulos]
        hoja.append_row(fila)

        # Añadir entrada en la hoja "productos"
        hoja_productos = sheet.worksheet("productos")
        hoja_productos.append_row([producto.id, producto.categoria])

        return {"message": "Producto agregado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/trazabilidad/{id_producto}")
async def get_trazabilidad_por_producto(id_producto: str):
    trazabilidad = find_trazabilidad_by_id(id_producto, 'id_producto')
    if trazabilidad:
        return trazabilidad
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trazabilidad not found",
    )

@router.get("/trazabilidad/proveniente/{id_producto_proveniente}")
async def get_trazabilidad_por_producto_proveniente(id_producto_proveniente: str):
    trazabilidad = find_trazabilidad_by_id(id_producto_proveniente, 'id_producto_proveniente')
    if trazabilidad:
        return trazabilidad
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trazabilidad not found",
    )
    
