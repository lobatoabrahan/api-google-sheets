from fastapi import HTTPException, status, APIRouter, Form, Depends
from pydantic import BaseModel, Field
from .sheets import connect_to_sheet
from uuid import uuid4
from datetime import datetime, date, timedelta
from typing import Dict, List
from typing import Union

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
    
def obtener_categorias():
    # Obtener la primera fila de la hoja de características que contiene los nombres de las categorías
    header_row = hoja_caracteristicas.row_values(1)
    categorias = list(set(header_row[1:]))  # Convertir el conjunto a una lista
    return categorias


def organizar_productos_por_categoria(categoria: str, categorias: List[str]):
    try:
        # Obtener todas las filas de la hoja de cálculo
        rows = hoja_caracteristicas.get_all_values()

        # Filtrar las filas que tienen la categoría especificada
        productos_originales = {}
        for row in rows[1:]:  # Ignorar la primera fila que contiene los encabezados
            id_producto = row[0]
            caracteristica = row[1]
            valor = row[2]

            # Verificar si ya existe una entrada para este producto
            if id_producto not in productos_originales:
                productos_originales[id_producto] = {'id_producto': id_producto, 'caracteristicas': {}}

            # Agregar la característica y valor al diccionario del producto
            productos_originales[id_producto]['caracteristicas'][caracteristica] = valor

        # Filtrar productos por la categoría especificada
        productos_categoria = [p for p in productos_originales.values() if p['caracteristicas'].get('categoria', '').lower() == categoria.lower()]

        if not productos_categoria:
            raise HTTPException(status_code=404, detail=f"No se encontraron productos para la categoría: {categoria}")

        return {"productos": productos_categoria}

    except Exception as e:
        print(f"Error al obtener productos por categoría: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/productos_por_categoria/{categoria}")
async def obtener_productos_por_categoria(categoria: str, categorias: List[str] = Depends(obtener_categorias)):
    return organizar_productos_por_categoria(categoria, categorias)