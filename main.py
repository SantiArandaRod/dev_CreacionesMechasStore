from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from DBengine import get_session, init_db
import operations as crud
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, title="Sistema de Inventario de Creaciones Mechas")


### Set de frontend
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


### Home Page
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ===== ENDPOINTS CATEGORÍAS =====
@app.post("/categorias/", status_code=status.HTTP_201_CREATED)
async def crear_categoria(categoria: dict, session: AsyncSession = Depends(get_session)):
    """Crear una nueva categoría - usando JSON en el body"""
    tipo = categoria.get("tipo")
    codigo = categoria.get("codigo")

    if not tipo or not codigo:
        raise HTTPException(status_code=400, detail="Se requieren los campos 'tipo' y 'codigo'")

    try:
        nueva_categoria = await crud.crear_categoria(session, tipo, codigo)
        return {"message": "Categoría creada exitosamente", "categoria": nueva_categoria}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando categoría: {str(e)}")


@app.get("/categorias/")
async def obtener_categorias(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    """Obtener todas las categorías"""
    categorias = await crud.obtener_todas_categorias(session, skip, limit)
    return {"categorias": categorias}


@app.get("/categorias/{categoria_id}")
async def obtener_categoria(categoria_id: int, session: AsyncSession = Depends(get_session)):
    """Obtener una categoría específica"""
    categoria = await crud.obtener_categoria_por_id(session, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@app.patch("/categorias/{categoria_id}")
async def actualizar_categoria(categoria_id: int, nombre: str = None, codigo: str = None,
                         session: AsyncSession = Depends(get_session)):
    """Actualizar una categoría"""
    categoria = await crud.actualizar_categoria(session, categoria_id, nombre, codigo)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": "Categoría actualizada exitosamente", "categoria": categoria}


@app.delete("/categorias/{categoria_id}")
async def eliminar_categoria(categoria_id: int, session: AsyncSession = Depends(get_session)):
    """Eliminar una categoría"""
    if await crud.eliminar_categoria(session, categoria_id):
        return {"message": "Categoría eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


# ===== ENDPOINTS PRODUCTOS =====
@app.post("/productos/", status_code=status.HTTP_201_CREATED)
async def crear_producto(id_producto: str, nombre: str, precio: float, stock: int, id_categoria: int,
                   session: AsyncSession = Depends(get_session)):
    """Crear un nuevo producto"""
    # Verificar que la categoría existe
    if not await crud.categoria_existe(session, id_categoria):
        raise HTTPException(status_code=400, detail="La categoría especificada no existe")

    try:
        producto = await crud.crear_producto(session, id_producto, nombre, precio, stock, id_categoria)
        return {"message": "Producto creado exitosamente", "producto": producto}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando producto: {str(e)}")


@app.get("/productos/")
async def obtener_productos(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    productos = await crud.obtener_todos_productos(session, skip, limit)
    return {"productos": productos, "total": len(productos)}


@app.get("/productos/pagina")
async def pagina_productos(request: Request, session: AsyncSession = Depends(get_session)):
    """Renderiza la página de productos con todos los datos precargados."""
    productos = await crud.obtener_todos_productos(session)
    categorias = await crud.obtener_todas_categorias(session)

    # Mapeo de categorías para obtener el nombre fácilmente
    # (ajusta la clave si tu modelo usa otro nombre para el id)
    categorias_dict = {getattr(c, "id_categoria", getattr(c, "id", None)): c.tipo for c in categorias}

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


@app.get("/productos/{producto_id}")
async def obtener_producto(producto_id: str, session: AsyncSession = Depends(get_session)):
    """Obtener un producto específico"""
    producto = await crud.obtener_producto_por_id(session, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.get("/productos/categoria/{categoria_id}")
async def obtener_productos_por_categoria(categoria_id: int, session: AsyncSession = Depends(get_session)):
    """Obtener productos de una categoría específica"""
    if not await crud.categoria_existe(session, categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    productos = await crud.obtener_productos_por_categoria(session, categoria_id)
    return {"productos": productos, "categoria_id": categoria_id, "total": len(productos)}


@app.put("/productos/{producto_id}")
async def actualizar_producto(
        producto_id: str,
        nombre: str = None,
        precio: float = None,
        stock: int = None,
        id_categoria: int = None,
        session: AsyncSession = Depends(get_session)
):
    """Actualizar un producto"""
    # Si se especifica nueva categoría, verificar que existe
    if id_categoria and not await crud.categoria_existe(session, id_categoria):
        raise HTTPException(status_code=400, detail="La categoría especificada no existe")

    producto = await crud.actualizar_producto(session, producto_id, nombre, precio, stock, id_categoria)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto actualizado exitosamente", "producto": producto}


# STOCK PRODUCTOS
@app.put("/productos/{producto_id}/stock")
async def actualizar_stock_producto(producto_id: str, nueva_cantidad: int, session: AsyncSession = Depends(get_session)):
    """Actualizar el stock de un producto, sea cual sea"""
    if nueva_cantidad < 0:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser negativa")

    producto = await crud.actualizar_stock_producto(session, producto_id, nueva_cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Stock actualizado a {nueva_cantidad}", "producto": producto}


@app.post("/productos/{producto_id}/agregar-stock")
async def agregar_stock(producto_id: str, cantidad: int, session: AsyncSession = Depends(get_session)):
    """Agregar stock a un producto (para compras)"""
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")

    producto = await crud.sumar_stock_producto(session, producto_id, cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Se agregaron {cantidad} unidades. Stock actual: {producto.stock}", "producto": producto}


@app.post("/productos/{producto_id}/quitar-stock")
async def quitar_stock(producto_id: str, cantidad: int, session: AsyncSession = Depends(get_session)):
    """Quitar stock de un producto (para ventas)"""
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")

    if not await crud.verificar_stock_disponible(session, producto_id, cantidad):
        raise HTTPException(status_code=400, detail="No hay suficiente stock disponible")

    producto = await crud.restar_stock_producto(session, producto_id, cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Se quitaron {cantidad} unidades. Stock actual: {producto.stock}", "producto": producto}


@app.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: str, session: AsyncSession = Depends(get_session)):
    """Eliminar un producto"""
    if await crud.eliminar_producto(session, producto_id):
        return {"message": "Producto eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


# ===== ENDPOINTS CLIENTES =====
@app.post("/clientes/", status_code=status.HTTP_201_CREATED)
async def crear_cliente(nombre: str, telefono: str, email: str, session: AsyncSession = Depends(get_session)):
    """Crear un nuevo cliente"""
    if await crud.buscar_cliente_por_email(session, email):
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese email")

    try:
        cliente = await crud.crear_cliente(session, nombre, telefono, email)
        return {"message": "Cliente creado exitosamente", "cliente": cliente}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando cliente: {str(e)}")


@app.get("/clientes/")
async def obtener_clientes(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    """Obtener todos los clientes"""
    clientes = await crud.obtener_todos_clientes(session, skip, limit)
    return {"clientes": clientes, "total": len(clientes)}


@app.get("/clientes/{cliente_id}")
async def obtener_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    """Obtener un cliente específico"""
    cliente = await crud.obtener_cliente_por_id(session, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.get("/clientes/email/{email}")
async def buscar_cliente_por_email(email: str, session: AsyncSession = Depends(get_session)):
    """Buscar cliente por email"""
    cliente = await crud.buscar_cliente_por_email(session, email)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.put("/clientes/{cliente_id}")
async def actualizar_cliente(cliente_id: int, nombre: str = None, telefono: str = None, email: str = None,
                       session: AsyncSession = Depends(get_session)):
    """Actualizar un cliente"""
    cliente = await crud.actualizar_cliente(session, cliente_id, nombre, telefono, email)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"message": "Cliente actualizado exitosamente", "cliente": cliente}


@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    """Eliminar un cliente"""
    if await crud.eliminar_cliente(session, cliente_id):
        return {"message": "Cliente eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")


# ===== ENDPOINTS PROVEEDORES =====
@app.get("/proveedores/pagina")
async def pagina_proveedores(request: Request, session: AsyncSession = Depends(get_session)):
    proveedores = await crud.obtener_proveedores_resumen(session)
    return templates.TemplateResponse(
        "proveedores.html",
        {"request": request, "proveedores": proveedores}
    )

@app.post("/proveedores/eliminar/{nit}")
async def eliminar_proveedor_html(nit: str, session: AsyncSession = Depends(get_session)):
    """Elimina un proveedor y redirige a la página de proveedores."""
    if await crud.mover_proveedor(session, nit):
        return RedirectResponse(url="/proveedores/pagina", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")


@app.get("/proveedoresE/")
async def pagina_proveedores_eliminados(request: Request, session: AsyncSession = Depends(get_session)):
    proveedores_eliminados = await crud.obtener_proveedores_eliminados(session)
    return templates.TemplateResponse(
        "proveedores_eliminados.html",
        {"request": request, "proveedores": proveedores_eliminados}
    )

@app.post("/proveedores/recuperar/{nit}")
async def recuperar_proveedor(nit: str, session: AsyncSession = Depends(get_session)):
    exito = await crud.recuperar_proveedor(session, nit)
    return RedirectResponse(url="/proveedoresE/", status_code=303)


@app.post("/proveedores/", status_code=status.HTTP_201_CREATED)
async def crear_proveedor(nit: str, nombre: str, contacto: str, direccion: str, ciudad: str,
                    session: AsyncSession = Depends(get_session)):
    """Crear un nuevo proveedor"""
    try:
        proveedor = await crud.crear_proveedor(session, nit, nombre, direccion, ciudad, contacto)
        return {"message": "Proveedor creado exitosamente", "proveedor": proveedor}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando proveedor: {str(e)}")


@app.get("/proveedores/")
async def obtener_proveedores(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    """Obtener todos los proveedores"""
    proveedores = await crud.obtener_todos_proveedores(session, skip, limit)
    return {"proveedores": proveedores, "total": len(proveedores)}


@app.get("/proveedores/{nit}")
async def obtener_proveedor(nit: str, session: AsyncSession = Depends(get_session)):
    """Obtener un proveedor específico"""
    proveedor = await crud.obtener_proveedor_por_nit(session, nit)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor

@app.put("/proveedores/{nit}")
async def actualizar_proveedor(nit: str, nombre: str = None, direccion: str = None, ciudad: str = None, contacto: str = None,
                         session: AsyncSession = Depends(get_session)):
    """Actualizar un proveedor"""
    proveedor = await crud.actualizar_proveedor(session, nit, nombre, direccion, ciudad, contacto)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor actualizado exitosamente", "proveedor": proveedor}

@app.delete("/proveedores/{nit}")
async def eliminar_proveedor(nit: str, session: AsyncSession = Depends(get_session)):
    """Eliminar proveedor"""
    if await crud.eliminar_proveedor(session, nit):
        return {"message": "Proveedor eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")


# ===== ENDPOINTS DE VENTAS =====
@app.get("/ventas/pagina")
async def pagina_ventas(request: Request):
    return templates.TemplateResponse("ventas.html", {"request": request})


# ===== ENDPOINTS DE COMPRAS =====
@app.get("/compras/pagina")
async def pagina_compras(request: Request):
    return templates.TemplateResponse("compras.html", {"request": request})


# ===== ENDPOINTS DE UTILIDAD =====
@app.get("/verificar/categoria/{categoria_id}")
async def verificar_categoria_existe(categoria_id: int, session: AsyncSession = Depends(get_session)):
    """Verificar si una categoría existe"""
    existe = await crud.categoria_existe(session, categoria_id)
    return {"categoria_id": categoria_id, "existe": existe}


@app.get("/verificar/producto/{producto_id}")
async def verificar_producto_existe(producto_id: str, session: AsyncSession = Depends(get_session)):
    """Verificar si un producto existe"""
    existe = await crud.producto_existe(session, producto_id)
    return {"producto_id": producto_id, "existe": existe}


@app.get("/verificar/stock/{producto_id}")
async def verificar_stock_disponible(producto_id: str, cantidad: int, session: AsyncSession = Depends(get_session)):
    """Verificar si hay suficiente stock para una cantidad específica"""
    disponible = await crud.verificar_stock_disponible(session, producto_id, cantidad)
    producto = await crud.obtener_producto_por_id(session, producto_id)
    stock_actual = producto.stock if producto else 0
    return {
        "producto_id": producto_id,
        "cantidad_requerida": cantidad,
        "stock_actual": stock_actual,
        "stock_suficiente": disponible
    }
