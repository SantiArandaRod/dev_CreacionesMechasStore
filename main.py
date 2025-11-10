from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from DBengine import get_session, init_db
import operations as crud
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# === EVENTO DE VIDA (LIFESPAN) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos al iniciar la app."""
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, title="Sistema de Inventario - Creaciones Mechas")

# === CONFIGURACIÓN DE FRONTEND ===
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === PÁGINA PRINCIPAL ===
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# === PÁGINAS HTML ===
@app.get("/proveedores/pagina")
async def pagina_proveedores(request: Request, session: AsyncSession = Depends(get_session)):
    proveedores = await crud.obtener_proveedores_resumen(session)
    return templates.TemplateResponse("proveedores.html", {"request": request, "proveedores": proveedores})

@app.get("/productos/pagina")
async def pagina_productos(request: Request, session: AsyncSession = Depends(get_session)):
    productos = await crud.obtener_todos_productos(session)
    categorias = await crud.obtener_todas_categorias(session)
    categorias_dict = {c.id_categoria: c.tipo for c in categorias}
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
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos": productos_lista,
        "categorias": categorias
    })

@app.get("/ventas/pagina")
async def pagina_ventas(request: Request):
    return templates.TemplateResponse("ventas.html", {"request": request})

@app.get("/compras/pagina")
async def pagina_compras(request: Request):
    return templates.TemplateResponse("compras.html", {"request": request})


# === CRUD DE CATEGORÍAS ===
@app.post("/categorias/", status_code=status.HTTP_201_CREATED)
async def crear_categoria(tipo: str = Form(...), codigo: str = Form(...), session: AsyncSession = Depends(get_session)):
    if not tipo or not codigo:
        raise HTTPException(status_code=400, detail="Faltan campos requeridos")
    try:
        nueva_categoria = await crud.crear_categoria(session, tipo, codigo)
        return {"message": "Categoría creada exitosamente", "categoria": nueva_categoria}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando categoría: {e}")

@app.get("/categorias/")
async def obtener_categorias(session: AsyncSession = Depends(get_session)):
    categorias = await crud.obtener_todas_categorias(session)
    return {"categorias": categorias}

@app.delete("/categorias/{categoria_id}")
async def eliminar_categoria(categoria_id: int, session: AsyncSession = Depends(get_session)):
    if await crud.eliminar_categoria(session, categoria_id):
        return {"message": "Categoría eliminada"}
    raise HTTPException(status_code=404, detail="Categoría no encontrada")


# === CRUD DE PRODUCTOS ===
@app.post("/productos/", status_code=status.HTTP_201_CREATED)
async def crear_producto(
    id_producto: str = Form(...),
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    id_categoria: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    if not await crud.categoria_existe(session, id_categoria):
        raise HTTPException(status_code=400, detail="Categoría no válida")
    try:
        producto = await crud.crear_producto(session, id_producto, nombre, precio, stock, id_categoria)
        return {"message": "Producto creado correctamente", "producto": producto}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")

@app.get("/productos/")
async def obtener_productos(session: AsyncSession = Depends(get_session)):
    productos = await crud.obtener_todos_productos(session)
    categorias = {c.id_categoria: c.tipo for c in await crud.obtener_todas_categorias(session)}
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
async def eliminar_producto(producto_id: str, session: AsyncSession = Depends(get_session)):
    if await crud.eliminar_producto(session, producto_id):
        return {"message": "Producto eliminado"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# === MANEJO DE STOCK ===
@app.put("/productos/{producto_id}/stock")
async def actualizar_stock(producto_id: str, nueva_cantidad: int, session: AsyncSession = Depends(get_session)):
    if nueva_cantidad < 0:
        raise HTTPException(status_code=400, detail="Cantidad negativa no permitida")
    producto = await crud.actualizar_stock_producto(session, producto_id, nueva_cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Stock actualizado: {nueva_cantidad}", "producto": producto}


# === CRUD DE CLIENTES ===
@app.post("/clientes/", status_code=status.HTTP_201_CREATED)
async def crear_cliente(nombre: str, telefono: str, email: str, session: AsyncSession = Depends(get_session)):
    if await crud.buscar_cliente_por_email(session, email):
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese email")
    cliente = await crud.crear_cliente(session, nombre, telefono, email)
    return {"message": "Cliente creado", "cliente": cliente}

@app.get("/clientes/")
async def obtener_clientes(session: AsyncSession = Depends(get_session)):
    clientes = await crud.obtener_todos_clientes(session)
    return {"clientes": clientes, "total": len(clientes)}


# === UTILIDADES ===
@app.get("/verificar/producto/{producto_id}")
async def verificar_producto_existe(producto_id: str, session: AsyncSession = Depends(get_session)):
    existe = await crud.producto_existe(session, producto_id)
    return {"producto_id": producto_id, "existe": existe}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
