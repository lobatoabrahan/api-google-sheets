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
sheet = connect_to_sheet("productos")

def obtener_producto_por_id(id_producto: str):
    # Obtén todos los productos de la base de datos
    productos = sheet.worksheet("productos").get_all_records()
    # Busca el producto con el ID dado
    producto = next((p for p in productos if p['id'] == id_producto), None)
    if producto:
        categoria = producto.get('categoria')
        if categoria:
            # Obtén todos los productos de la categoría de la base de datos
            productos_categoria = sheet.worksheet(categoria).get_all_records()
            # Busca el producto con el ID dado en la categoría
            producto_categoria = next((p for p in productos_categoria if p['id'] == id_producto), None)
            if producto_categoria:
                producto_categoria['categoria'] = categoria
                id_producto_proveniente = producto_categoria.get('id_producto_proveniente')
                while id_producto_proveniente:
                    producto_proveniente = obtener_producto_por_id(id_producto_proveniente)
                    if producto_proveniente:
                        # Eliminar las columnas duplicadas
                        producto_proveniente = {k: v for k, v in producto_proveniente.items() if k not in producto_categoria}
                        # Fusionar la información del producto proveniente
                        producto_categoria.update(producto_proveniente)
                        id_producto_proveniente = producto_proveniente.get('id_producto_proveniente')
                return producto_categoria
    return None

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

def buscar_id_en_productos(id_producto: str):
    # Obtén todos los productos de la base de datos
    productos = sheet.worksheet("productos").get_all_records()
    # Busca el producto con el ID dado
    producto = next((p for p in productos if p['id'] == id_producto), None)
    return producto

def find_producto_by_id(id: str):
    # Obtén todos los productos de la base de datos
    productos = sheet.worksheet("productos").get_all_records()
    # Busca el producto con el ID dado
    producto = next((p for p in productos if p['id'] == id), None)

    # Buscar el producto en la hoja de su categoría
    hoja_categoria = sheet.worksheet(producto['categoria'])
    filas_categoria = hoja_categoria.get_all_values()
    titulos_categoria = filas_categoria[0]
    id_index_categoria = titulos_categoria.index('id')

    especificaciones = None
    for fila in filas_categoria[1:]:
        if fila[id_index_categoria] == id:
            especificaciones = dict(zip(titulos_categoria, fila))
            break

    return especificaciones

@router.get("/productos")
async def get_productos(limit: int = None):
    try:
        productos = sheet.worksheet("productos").get_all_records()
        if limit is not None:
            productos = productos[:limit]
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/producto/{id}")
async def get_product_by_id(id: str):
    try:
        producto = obtener_producto_por_id(id)
        if producto:
            # Añadir la nueva funcionalidad
            productos_provenientes = await get_producto_con_provenientes_y_categorias_by_id(id)
            producto['productos_provenientes'] = productos_provenientes

            return producto
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def get_producto_con_provenientes(id_producto: str):
    producto = find_producto_by_id(id_producto)
    if producto:
        id_producto_proveniente = producto.get('id_producto_proveniente')
        if id_producto_proveniente:
            producto_proveniente = await get_producto_con_provenientes(id_producto_proveniente)
            if producto_proveniente:
                # Eliminar las columnas duplicadas
                producto_proveniente = {k: v for k, v in producto_proveniente.items() if k not in producto}
                # Fusionar la información del producto proveniente
                producto.update(producto_proveniente)
    return producto

async def get_lista_productos_provenientes(id_producto: str):
    productos_provenientes = []
    id_producto_proveniente = id_producto

    while id_producto_proveniente:
        producto_proveniente = find_producto_by_id(id_producto_proveniente)
        if producto_proveniente:
            productos_provenientes.append(producto_proveniente)
            id_producto_proveniente = producto_proveniente.get('id_producto_proveniente')
        else:
            break

    return productos_provenientes

@router.get("/producto/{id}/provenientes")
async def get_productos_provenientes(id: str):
    try:
        producto = await get_producto_con_provenientes(id)
        return producto
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/productos/{categoria}")
async def get_bobinas(categoria: str, limit: int = None):
    try:
        productos = sheet.worksheet(categoria).get_all_records()
        for producto in productos:
            id_producto_proveniente = producto.get('id_producto_proveniente')
            if id_producto_proveniente:
                producto_proveniente = await get_producto_con_provenientes(id_producto_proveniente)
                if producto_proveniente:
                    # Eliminar las columnas duplicadas
                    producto_proveniente = {k: v for k, v in producto_proveniente.items() if k not in producto}
                    # Fusionar la información del producto proveniente
                    producto.update(producto_proveniente)
        if limit is not None:
            productos = productos[:limit]
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def find_categoria_by_id(id_producto: str):
    productos = sheet.worksheet("productos").get_all_records()
    for producto in productos:
        if producto['id'] == id_producto:
            return producto['categoria']
    return None
    
async def get_producto_con_provenientes_by_id(id_producto: str, productos_provenientes=None):
    if productos_provenientes is None:
        productos_provenientes = []
    producto = find_producto_by_id(id_producto)
    if producto:
        id_producto_proveniente = producto.get('id_producto_proveniente')
        if id_producto_proveniente and id_producto_proveniente not in productos_provenientes:
            productos_provenientes.append(id_producto_proveniente)
            producto_proveniente = await get_producto_con_provenientes_by_id(id_producto_proveniente, productos_provenientes)
            if producto_proveniente:
                # Eliminar las columnas duplicadas
                producto_proveniente = {k: v for k, v in producto_proveniente.items() if k not in producto}
                # Fusionar la información del producto proveniente
                producto.update(producto_proveniente)
    return producto
    

async def get_producto_con_provenientes_y_categorias_by_id(id_producto: str):
    # Buscar el producto por su ID
    producto = buscar_id_en_productos(id_producto)
    if not producto:
        return None

    # Inicializar la lista de productos provenientes
    productos_provenientes = []

    # Obtener el ID del producto proveniente
    id_producto_proveniente = producto.get('id_producto_proveniente')

    # Mientras haya un ID de producto proveniente y no sea el mismo que el ID del producto
    while id_producto_proveniente and id_producto_proveniente != id_producto:
        # Buscar el producto proveniente por su ID
        producto_proveniente = buscar_id_en_productos(id_producto_proveniente)
        if producto_proveniente:
            # Obtener la categoría del producto proveniente
            categoria_proveniente = find_categoria_by_id(id_producto_proveniente)
            if categoria_proveniente:
                # Agregar la categoría al producto proveniente
                producto_proveniente['categoria'] = categoria_proveniente
            # Agregar el producto proveniente a la lista de productos provenientes
            productos_provenientes.append(producto_proveniente)
            # Obtener el ID del siguiente producto proveniente
            id_producto_proveniente = producto_proveniente.get('id_producto_proveniente')
        else:
            break

    # Agregar la lista de productos provenientes al producto
    producto['productos_provenientes'] = productos_provenientes

    return producto

@router.get("/producto/{categoria}/{id}")
async def get_producto(categoria: str, id: str):
    try:
        producto = find_producto_by_id(id)
        if producto:
            producto_proveniente = await get_producto_con_provenientes_by_id(producto['id_producto_proveniente'])
            if producto_proveniente:
                # Eliminar las columnas duplicadas
                producto_proveniente = {k: v for k, v in producto_proveniente.items() if k not in producto}
                # Fusionar la información del producto proveniente
                producto.update(producto_proveniente)

            # Añadir la nueva funcionalidad
            producto_con_provenientes_y_categorias = await get_producto_con_provenientes_y_categorias_by_id(id)
            if producto_con_provenientes_y_categorias:
                producto['productos_provenientes_y_categorias'] = producto_con_provenientes_y_categorias['productos_provenientes']

            return producto
        else:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/producto")
async def add_producto(producto: Dict = Form(...)):
    try:
        hoja = sheet.worksheet(producto.categoria)
        producto_dict = producto.dict()
        titulos = hoja.row_values(1)  # Asume que los títulos están en la primera fila
        producto_dict['id'] = str(uuid4())  # Añadir el id al producto

        

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
        hoja_productos.append_row([producto_dict['id'], producto.categoria])

        return {"message": "Producto agregado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/trazabilidad/{id_producto}")
async def get_trazabilidad_por_producto(id_producto: str):
    trazabilidades = find_trazabilidad_by_id(id_producto, 'id_producto')
    productos_provenientes = []
    for trazabilidad in trazabilidades:
        id_producto_proveniente = trazabilidad.get('id_producto_proveniente')
        if id_producto_proveniente:
            producto_proveniente = find_producto_by_id(id_producto_proveniente)
            if producto_proveniente:
                productos_provenientes.append(producto_proveniente)
    if productos_provenientes:
        return {"trazabilidades": trazabilidades, "productos_provenientes": productos_provenientes}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trazabilidad o producto proveniente no encontrados",
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
    
