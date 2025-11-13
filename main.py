from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from DBengine import get_session, init_db
import operations as crud
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os

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

@app.get("/productos/buscar")
async def buscar_productos_endpoint(
    query: str,
    session: AsyncSession = Depends(get_session)
):
    resultados = await crud.buscar_productos(session, query)
    return {"resultados": resultados, "total": len(resultados)}


@app.get("/productos/paginados/")
async def productos_paginados(
    page: int = 1,
    page_size: int = 10,
    categoria: int = 0,
    search: str = "",
    session: AsyncSession = Depends(get_session)
):
    productos_filtrados = await crud.obtener_productos_filtrados(
        session, categoria=categoria, search=search
    )

    pagina, total = crud.paginar_lista(productos_filtrados, page, page_size)

    productos_formateados = await crud.formatear_productos(session, pagina)

    total_pages = (total + page_size - 1) // page_size

    return {
        "productos": productos_formateados,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }


@app.get("/productos/categoria/{categoria_id}")
async def obtener_productos_por_categoria(categoria_id: int, session: AsyncSession = Depends(get_session)):
    """
    Devuelve todos los productos de una categoría específica.
    Si categoria_id == 0, devuelve todos los productos.
    """
    if categoria_id == 0:
        productos = await crud.obtener_todos_productos(session)
    else:
        productos = await crud.obtener_productos_por_categoria(session, categoria_id)

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
# === CRUD DE PROVEEDORES ===
@app.post("/proveedores/", status_code=status.HTTP_201_CREATED)
async def crear_proveedor(
    nit: str = Form(...),
    nombre: str = Form(...),
    direccion: str = Form(...),
    ciudad: str = Form(...),
    contacto: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Crea un nuevo proveedor"""
    try:
        if await crud.proveedor_existe(session, nit):
            raise HTTPException(status_code=400, detail="El proveedor ya existe")

        proveedor = await crud.crear_proveedor(session, nit, nombre, direccion, ciudad, contacto)
        return {"message": "Proveedor agregado exitosamente", "proveedor": proveedor}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando proveedor: {e}")


@app.get("/proveedores/")
async def obtener_proveedores(session: AsyncSession = Depends(get_session)):
    """Devuelve todos los proveedores"""
    proveedores = await crud.obtener_todos_proveedores(session)
    return {"proveedores": proveedores, "total": len(proveedores)}


@app.delete("/proveedores/{nit}")
async def eliminar_proveedor(nit: str, session: AsyncSession = Depends(get_session)):
    """Elimina un proveedor (mueve a backup)"""
    if await crud.mover_proveedor(session, nit):
        return {"message": "Proveedor movido al backup"}
    raise HTTPException(status_code=404, detail="Proveedor no encontrado")


@app.get("/proveedores/backup/")
async def obtener_proveedores_backup(session: AsyncSession = Depends(get_session)):
    """Devuelve los proveedores eliminados (backup)"""
    proveedores_backup = await crud.obtener_proveedores_eliminados(session)
    return {"backup": proveedores_backup}

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
@app.get("/clientes/pagina")
async def pagina_clientes(request: Request, session: AsyncSession = Depends(get_session)):
    clientes = await crud.obtener_todos_clientes(session)
    return templates.TemplateResponse(
        "clientes.html",
        {"request": request, "clientes": clientes}
    )

@app.post("/clientes/", status_code=status.HTTP_201_CREATED)
async def crear_cliente(
    nombre: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    if await crud.buscar_cliente_por_email(session, email):
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese email")

    cliente = await crud.crear_cliente(session, nombre, telefono, email)
    return {"message": "Cliente creado", "cliente": cliente}
@app.get("/clientes/")
async def obtener_clientes(session: AsyncSession = Depends(get_session)):
    clientes = await crud.obtener_todos_clientes(session)
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


@app.post("/clientes/{cliente_id}/inactivar")
async def inactivar_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    cliente = await crud.actualizar_cliente(session, cliente_id, activo=False)
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")
    return RedirectResponse("/clientes/pagina", status_code=303)

@app.post("/clientes/{cliente_id}/activar")
async def activar_cliente(cliente_id: int, session: AsyncSession = Depends(get_session)):
    cliente = await crud.actualizar_cliente(session, cliente_id, activo=True)
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")
    return RedirectResponse("/clientes/pagina", status_code=303)


# ===== ENDPOINTS PROVEEDORES =====

# Página HTML principal de proveedores
@app.get("/proveedores/pagina")
async def pagina_proveedores(request: Request, session: AsyncSession = Depends(get_session)):
    proveedores = await crud.obtener_proveedores_resumen(session)
    return templates.TemplateResponse(
        "proveedores.html",
        {"request": request, "proveedores": proveedores}
    )


# Crear proveedor (desde formulario HTML)
@app.post("/proveedores/", status_code=status.HTTP_201_CREATED)
async def crear_proveedor_endpoint(
    nit: str = Form(...),
    nombre: str = Form(...),
    contacto: str = Form(...),
    direccion: str = Form(...),
    ciudad: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        nuevo = await crud.crear_proveedor(
            session, nit, nombre, direccion, ciudad, contacto
        )
        return {"message": "Proveedor creado", "proveedor": nuevo}

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


# Eliminar proveedor moviéndolo a backup
@app.post("/proveedores/eliminar/{nit}")
async def eliminar_proveedor_html(nit: str, session: AsyncSession = Depends(get_session)):
    if await crud.mover_proveedor(session, nit):
        return RedirectResponse(url="/proveedores/pagina", status_code=303)
    raise HTTPException(status_code=404, detail="Proveedor no encontrado")


# Página HTML de proveedores eliminados
@app.get("/proveedoresE/")
async def pagina_proveedores_eliminados(request: Request, session: AsyncSession = Depends(get_session)):
    proveedores_eliminados = await crud.obtener_proveedores_eliminados(session)
    return templates.TemplateResponse(
        "proveedores_eliminados.html",
        {"request": request, "proveedores": proveedores_eliminados}
    )


# Recuperar proveedor desde backup
@app.post("/proveedores/recuperar/{nit}")
async def recuperar_proveedor(nit: str, session: AsyncSession = Depends(get_session)):
    await crud.recuperar_proveedor(session, nit)
    return RedirectResponse(url="/proveedoresE/", status_code=303)


# API JSON: obtener todos los proveedores
@app.get("/proveedores/")
async def obtener_proveedores(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    proveedores = await crud.obtener_todos_proveedores(session, skip, limit)
    return {"proveedores": proveedores, "total": len(proveedores)}


# API JSON: actualizar proveedor
@app.put("/proveedores/{nit}")
async def actualizar_proveedor(
    nit: str,
    nombre: str = None,
    direccion: str = None,
    ciudad: str = None,
    contacto: str = None,
    session: AsyncSession = Depends(get_session)
):
    proveedor = await crud.actualizar_proveedor(session, nit, nombre, direccion, ciudad, contacto)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor actualizado exitosamente", "proveedor": proveedor}

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

# === PÁGINA Y ENDPOINT DE HACER VENTA ===

@app.get("/ventas/hacer_venta")
async def pagina_hacer_venta(request: Request, session: AsyncSession = Depends(get_session)):
    """Página para registrar una venta"""
    clientes = await crud.obtener_todos_clientes(session)
    productos = await crud.obtener_todos_productos(session)
    return templates.TemplateResponse("hacer_venta.html", {
        "request": request,
        "clientes": clientes,
        "productos": productos
    })


@app.post("/ventas/hacer")
async def realizar_venta(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Endpoint robusto que acepta múltiples productos.
    Recibe form; usa form.getlist('producto_id') y form.getlist('cantidad').
    """
    form = await request.form()

    # cliente
    cliente_id = form.get("cliente_id")
    if not cliente_id:
        raise HTTPException(status_code=400, detail="Falta seleccionar cliente")

    # obtenemos listas de productos y cantidades de manera robusta
    producto_ids = form.getlist("producto_id")
    cantidades_raw = form.getlist("cantidad")

    # Si alguna vez el navegador envía con sufijo '[]' (por si quedó alguna plantilla antigua),
    # también intentamos obtener esas keys:
    if (not producto_ids or not cantidades_raw):
        # buscar claves que contengan 'producto_id' o 'producto_id[]'
        producto_ids = producto_ids or [v for k, v in form.items() if k.startswith("producto_id")]
        cantidades_raw = cantidades_raw or [v for k, v in form.items() if k.startswith("cantidad")]

    if not producto_ids or not cantidades_raw or len(producto_ids) == 0:
        raise HTTPException(status_code=400, detail="Faltan productos en el formulario")

    if len(producto_ids) != len(cantidades_raw):
        raise HTTPException(status_code=400, detail="Productos y cantidades desbalanceadas")

    # convertir cantidades a int y validar
    try:
        cantidades = [int(x) for x in cantidades_raw]
    except Exception:
        raise HTTPException(status_code=400, detail="Cantidad inválida en formulario")

    # Validar cliente
    cliente = await crud.obtener_cliente_por_id(session, int(cliente_id))
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Construir lista de tuples (producto_id, cantidad) y validar stock
    productos_para_venta = []
    for pid, qty in zip(producto_ids, cantidades):
        if qty <= 0:
            raise HTTPException(status_code=400, detail=f"Cantidad inválida para producto {pid}")

        producto = await crud.obtener_producto_por_id(session, pid)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto no encontrado (id: {pid})")

        if not await crud.verificar_stock_disponible(session, pid, qty):
            raise HTTPException(status_code=400, detail=f"No hay suficiente stock para {producto.nombre}")

        productos_para_venta.append((pid, qty))

    # Llamar a operations.crear_venta_txt (que actualizará stock y generará el TXT)
    nombre_archivo = await crud.crear_venta_txt(session, cliente.nombre, str(cliente.id_cliente), productos_para_venta)

    # Renderizar vista de éxito mostrando lista de vendidos y ruta del archivo
    return templates.TemplateResponse("venta_exitosa.html", {
        "request": request,
        "cliente": cliente,
        "productos": productos_para_venta,
        "archivo": nombre_archivo
    })
@app.get("/ventas/historial_ventas")
async def historial_ventas(request: Request):
    ruta_ventas = "ventas_txt"
    ventas = []

    # Si la carpeta existe, leer los archivos .txt
    if os.path.exists(ruta_ventas):
        for archivo in os.listdir(ruta_ventas):
            if archivo.endswith(".txt"):
                ruta_archivo = os.path.join(ruta_ventas, archivo)
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                ventas.append({"nombre": archivo, "contenido": contenido})

    return templates.TemplateResponse(
        "historial_ventas.html",
        {"request": request, "ventas": ventas}
    )