
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from DBengine import get_session, init_db
import operations as crud

app = FastAPI(title="Sistema de Inventario creaciones mechas - Backend Modular")


# Inicializar DB al arrancar
@app.on_event("startup")
def startup_event():
    init_db()


# Endpoint básico de prueba
@app.get("/")
def root():
    return {"message": "Backend corriendo correctamente"}


# ===== ENDPOINTS CATEGORÍAS =====
@app.post("/categorias/", status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: dict, session: Session = Depends(get_session)):
    """Crear una nueva categoría - usando JSON en el body"""
    tipo = categoria.get("tipo")
    codigo = categoria.get("codigo")

    if not tipo or not codigo:
        raise HTTPException(status_code=400, detail="Se requieren los campos 'tipo' y 'codigo'")

    try:
        nueva_categoria = crud.crear_categoria(session, tipo, codigo)
        return {"message": "Categoría creada exitosamente", "categoria": nueva_categoria}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando categoría: {str(e)}")


@app.get("/categorias/")
def obtener_categorias(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Obtener todas las categorías"""
    categorias = crud.obtener_todas_categorias(session, skip, limit)
    return {"categorias": categorias}


@app.get("/categorias/{categoria_id}")
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    """Obtener una categoría específica"""
    categoria = crud.obtener_categoria_por_id(session, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@app.put("/categorias/{categoria_id}")
def actualizar_categoria(categoria_id: int, nombre: str = None, codigo: str = None,
                         session: Session = Depends(get_session)):
    """Actualizar una categoría"""
    categoria = crud.actualizar_categoria(session, categoria_id, nombre, codigo)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": "Categoría actualizada exitosamente", "categoria": categoria}


@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    """Eliminar una categoría"""
    if crud.eliminar_categoria(session, categoria_id):
        return {"message": "Categoría eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


# ===== ENDPOINTS PRODUCTOS =====
@app.post("/productos/", status_code=status.HTTP_201_CREATED)
def crear_producto(id_producto: str, nombre: str, precio: float, stock: int, id_categoria: int,
                   session: Session = Depends(get_session)):
    """Crear un nuevo producto"""
    # Verificar que la categoría existe
    if not crud.categoria_existe(session, id_categoria):
        raise HTTPException(status_code=400, detail="La categoría especificada no existe")

    try:
        producto = crud.crear_producto(session, id_producto, nombre, precio, stock, id_categoria)
        return {"message": "Producto creado exitosamente", "producto": producto}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando producto: {str(e)}")


@app.get("/productos/")
def obtener_productos(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Obtener todos los productos"""
    productos = crud.obtener_todos_productos(session, skip, limit)
    return {"productos": productos, "total": len(productos)}


@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: str, session: Session = Depends(get_session)):
    """Obtener un producto específico"""
    producto = crud.obtener_producto_por_id(session, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.get("/productos/categoria/{categoria_id}")
def obtener_productos_por_categoria(categoria_id: int, session: Session = Depends(get_session)):
    """Obtener productos de una categoría específica"""
    if not crud.categoria_existe(session, categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    productos = crud.obtener_productos_por_categoria(session, categoria_id)
    return {"productos": productos, "categoria_id": categoria_id, "total": len(productos)}


@app.put("/productos/{producto_id}")
def actualizar_producto(
        producto_id: str,
        nombre: str = None,
        precio: float = None,
        stock: int = None,
        id_categoria: int = None,
        session: Session = Depends(get_session)
):
    """Actualizar un producto"""
    # Si se especifica nueva categoría, verificar que existe
    if id_categoria and not crud.categoria_existe(session, id_categoria):
        raise HTTPException(status_code=400, detail="La categoría especificada no existe")

    producto = crud.actualizar_producto(session, producto_id, nombre, precio, stock, id_categoria)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto actualizado exitosamente", "producto": producto}


@app.put("/productos/{producto_id}/stock")
def actualizar_stock_producto(producto_id: str, nueva_cantidad: int, session: Session = Depends(get_session)):
    """Actualizar el stock de un producto"""
    if nueva_cantidad < 0:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser negativa")

    producto = crud.actualizar_stock_producto(session, producto_id, nueva_cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Stock actualizado a {nueva_cantidad}", "producto": producto}


@app.post("/productos/{producto_id}/agregar-stock")
def agregar_stock(producto_id: str, cantidad: int, session: Session = Depends(get_session)):
    """Agregar stock a un producto (para compras)"""
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")

    producto = crud.sumar_stock_producto(session, producto_id, cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Se agregaron {cantidad} unidades. Stock actual: {producto.stock}", "producto": producto}


@app.post("/productos/{producto_id}/quitar-stock")
def quitar_stock(producto_id: str, cantidad: int, session: Session = Depends(get_session)):
    """Quitar stock de un producto (para ventas)"""
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")

    if not crud.verificar_stock_disponible(session, producto_id, cantidad):
        raise HTTPException(status_code=400, detail="No hay suficiente stock disponible")

    producto = crud.restar_stock_producto(session, producto_id, cantidad)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": f"Se quitaron {cantidad} unidades. Stock actual: {producto.stock}", "producto": producto}


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: str, session: Session = Depends(get_session)):
    """Eliminar un producto"""
    if crud.eliminar_producto(session, producto_id):
        return {"message": "Producto eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


# ===== ENDPOINTS CLIENTES =====
@app.post("/clientes/", status_code=status.HTTP_201_CREATED)
def crear_cliente(nombre: str, telefono: str, email: str, session: Session = Depends(get_session)):
    """Crear un nuevo cliente"""
    if crud.buscar_cliente_por_email(session, email):
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese email")

    try:
        cliente = crud.crear_cliente(session, nombre, telefono, email)
        return {"message": "Cliente creado exitosamente", "cliente": cliente}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando cliente: {str(e)}")


@app.get("/clientes/")
def obtener_clientes(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Obtener todos los clientes"""
    clientes = crud.obtener_todos_clientes(session, skip, limit)
    return {"clientes": clientes, "total": len(clientes)}


@app.get("/clientes/{cliente_id}")
def obtener_cliente(cliente_id: int, session: Session = Depends(get_session)):
    """Obtener un cliente específico"""
    cliente = crud.obtener_cliente_por_id(session, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.get("/clientes/email/{email}")
def buscar_cliente_por_email(email: str, session: Session = Depends(get_session)):
    """Buscar cliente por email"""
    cliente = crud.buscar_cliente_por_email(session, email)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.put("/clientes/{cliente_id}")
def actualizar_cliente(cliente_id: int, nombre: str = None, telefono: str = None, email: str = None,
                       session: Session = Depends(get_session)):
    """Actualizar un cliente"""
    cliente = crud.actualizar_cliente(session, cliente_id, nombre, telefono, email)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"message": "Cliente actualizado exitosamente", "cliente": cliente}


@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    """Eliminar un cliente"""
    if crud.eliminar_cliente(session, cliente_id):
        return {"message": "Cliente eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")


# ===== ENDPOINTS PROVEEDORES =====
@app.post("/proveedores/", status_code=status.HTTP_201_CREATED)
def crear_proveedor(nit: str, nombre: str, contacto: str, direccion: str, ciudad: str,
                    session: Session = Depends(get_session)):
    """Crear un nuevo proveedor"""
    try:
        proveedor = crud.crear_proveedor(session, nit, nombre, direccion, ciudad, contacto)
        return {"message": "Proveedor creado exitosamente", "proveedor": proveedor}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando proveedor: {str(e)}")


@app.get("/proveedores/")
def obtener_proveedores(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Obtener todos los proveedores"""
    proveedores = crud.obtener_todos_proveedores(session, skip, limit)
    return {"proveedores": proveedores, "total": len(proveedores)}


@app.get("/proveedores/{nit}")
def obtener_proveedor(nit: str, session: Session = Depends(get_session)):
    """Obtener un proveedor específico"""
    proveedor = crud.obtener_proveedor_por_nit(session, nit)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


# ===== ENDPOINTS DE UTILIDAD =====
@app.get("/verificar/categoria/{categoria_id}")
def verificar_categoria_existe(categoria_id: int, session: Session = Depends(get_session)):
    """Verificar si una categoría existe"""
    existe = crud.categoria_existe(session, categoria_id)
    return {"categoria_id": categoria_id, "existe": existe}


@app.get("/verificar/producto/{producto_id}")
def verificar_producto_existe(producto_id: str, session: Session = Depends(get_session)):
    """Verificar si un producto existe"""
    existe = crud.producto_existe(session, producto_id)
    return {"producto_id": producto_id, "existe": existe}


@app.get("/verificar/stock/{producto_id}")
def verificar_stock_disponible(producto_id: str, cantidad: int, session: Session = Depends(get_session)):
    """Verificar si hay suficiente stock para una cantidad específica"""
    disponible = crud.verificar_stock_disponible(session, producto_id, cantidad)
    producto = crud.obtener_producto_por_id(session, producto_id)
    stock_actual = producto.stock if producto else 0
    return {
        "producto_id": producto_id,
        "cantidad_requerida": cantidad,
        "stock_actual": stock_actual,
        "stock_suficiente": disponible
    }
@app.put("/proveedores/{nit}")
def actualizar_proveedor(nit:str, nombre: str = None, direccion:str = None, ciudad:str = None, contacto:str = None,
                         session: Session = Depends(get_session)):
    """Actualizar un proveedor"""
    proveedor= crud.actualizar_proveedor(session,nit,nombre,direccion,ciudad,contacto)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor actualizado exitosamente", "proveedor": proveedor}
@app.delete("/proveedores/{nit}")
def eliminar_proveedor(nit:str, session: Session = Depends(get_session)):
    """Eliminar proveedor"""
    if crud.eliminar_proveedor(session,nit):
        return {"message": "Proveedor eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
