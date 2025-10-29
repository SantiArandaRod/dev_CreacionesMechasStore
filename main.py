from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from sqlmodel import Session
from DBengine import get_session, init_db
import operations as crud
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from modelSQL import Producto, Categoria

app = FastAPI(title="Sistema de Inventario - Creaciones Mechas")

# === CONFIGURACIÓN DE FRONTEND ===
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === EVENTO INICIAL ===
@app.on_event("startup")
def startup_event():
    init_db()

# === PÁGINA PRINCIPAL ===
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# === PÁGINAS ===
@app.get("/proveedores/pagina")
def pagina_proveedores(request: Request, session: Session = Depends(get_session)):
    proveedores = crud.obtener_proveedores_resumen(session)
    return templates.TemplateResponse(
        "proveedores.html",
        {"request": request, "proveedores": proveedores}
    )

@app.get("/productos/pagina")
def pagina_productos(request: Request, session: Session = Depends(get_session)):
    """Renderiza la página de productos con todos los datos precargados."""
    productos = crud.obtener_todos_productos(session)
    categorias = crud.obtener_todas_categorias(session)

    # Mapeo de categorías para obtener el nombre fácilmente
    categorias_dict = {c.id_categoria: c.tipo for c in categorias}

    # Adaptamos los productos para que incluyan el nombre de la categoría
    productos_lista = [
        {
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "id_categoria": p.id_categoria,
            "categoria_nombre": categorias_dict.get(p.id_categoria, "Sin categoría")
        }
        for p in productos
    ]

    return templates.TemplateResponse(
        "productos.html",
        {
            "request": request,
            "productos": productos_lista,
            "categorias": categorias
        }
    )

@app.get("/ventas/pagina")
def pagina_ventas(request: Request):
    return templates.TemplateResponse("ventas.html", {"request": request})

@app.get("/compras/pagina")
def pagina_compras(request: Request):
    return templates.TemplateResponse("compras.html", {"request": request})


# === CRUD DE CATEGORÍAS ===
@app.post("/categorias/", status_code=status.HTTP_201_CREATED)
def crear_categoria(tipo: str = Form(...), codigo: str = Form(...), session: Session = Depends(get_session)):
    if not tipo or not codigo:
        raise HTTPException(status_code=400, detail="Faltan campos requeridos")
    try:
        nueva_categoria = crud.crear_categoria(session, tipo, codigo)
        return {"message": "Categoría creada exitosamente", "categoria": nueva_categoria}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando categoría: {e}")

@app.get("/categorias/")
def obtener_categorias(session: Session = Depends(get_session)):
    return {"categorias": crud.obtener_todas_categorias(session)}

@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    if crud.eliminar_categoria(session, categoria_id):
        return {"message": "Categoría eliminada"}
    raise HTTPException(status_code=404, detail="Categoría no encontrada")


# === CRUD DE PRODUCTOS ===
@app.post("/productos/", status_code=status.HTTP_201_CREATED)
def crear_producto(
    id_producto: str = Form(...),
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    id_categoria: int = Form(...),
    session: Session = Depends(get_session)
):
    """Crear producto desde formulario."""
    if not crud.categoria_existe(session, id_categoria):
        raise HTTPException(status_code=400, detail="Categoría no válida")

    try:
        producto = crud.crear_producto(session, id_producto, nombre, precio, stock, id_categoria)
        return {"message": "Producto creado correctamente", "producto": producto}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")

@app.get("/productos/")
def obtener_productos(session: Session = Depends(get_session)):
    productos = crud.obtener_todos_productos(session)
    categorias = {c.id_categoria: c.tipo for c in crud.obtener_todas_categorias(session)}
    productos_lista = [
        {
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "id_categoria": p.id_categoria,
            "categoria_nombre": categorias.get(p.id_categoria, "Sin categoría")
        }
        for p in productos
    ]
    return {"productos": productos_lista, "total": len(productos_lista)}

@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: str, session: Session = Depends(get_session)):
    if crud.eliminar_producto(session, producto_id):
        return {"message": "Producto eliminado"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# === MANEJO DE STOCK ===
@app.put("/productos/{producto_id}/stock")
def actualizar_stock(producto_id: str, nueva_cantidad: int, session: Session = Depends(get_session)):
    if nueva_cantidad < 0:
        raise HTTPException(status_code=400, detail="Cantidad negativa no permitida")
    producto = crud.actualizar_stock_producto(session, producto_id, nueva_cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Stock actualizado: {nueva_cantidad}", "producto": producto}

# === FILTRAR PRODUCTOS POR CATEGORÍA ===
@app.get("/productos/categoria/{categoria_id}")
def obtener_productos_por_categoria(categoria_id: int, session: Session = Depends(get_session)):
    """
    Devuelve todos los productos pertenecientes a una categoría específica.
    Si categoria_id = 0, devuelve todos los productos.
    """
    # Si se pide "todas las categorías" (id=0)
    if categoria_id == 0:
        productos = crud.obtener_todos_productos(session)
    else:
        if not crud.categoria_existe(session, categoria_id):
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        productos = crud.obtener_productos_por_categoria(session, categoria_id)

    categorias = {c.id_categoria: c.tipo for c in crud.obtener_todas_categorias(session)}
    productos_lista = [
        {
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "id_categoria": p.id_categoria,
            "categoria_nombre": categorias.get(p.id_categoria, "Sin categoría")
        }
        for p in productos
    ]
    return {"productos": productos_lista, "total": len(productos_lista)}

# === EJECUCIÓN LOCAL ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
