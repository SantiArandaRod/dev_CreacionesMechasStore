from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from modelSQL import Categoria, Producto, Cliente, Proveedor, ProveedorBackup

# ===== CATEGORÍAS =====

async def crear_categoria(session: AsyncSession, tipo: str, codigo: str) -> Categoria:
    categoria = Categoria(tipo=tipo, codigo=codigo)
    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)
    return categoria

async def obtener_categoria_por_id(session: AsyncSession, categoria_id: int) -> Optional[Categoria]:
    return await session.get(Categoria, categoria_id)

async def obtener_todas_categorias(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Categoria]:
    result = await session.execute(select(Categoria).offset(skip).limit(limit))
    return result.scalars().all()

async def actualizar_categoria(session: AsyncSession, categoria_id: int, tipo: str = None, codigo: str = None) -> Optional[Categoria]:
    categoria = await session.get(Categoria, categoria_id)
    if categoria:
        if tipo is not None:
            categoria.tipo = tipo
        if codigo is not None:
            categoria.codigo = codigo
        await session.commit()
        await session.refresh(categoria)
    return categoria

async def eliminar_categoria(session: AsyncSession, categoria_id: int) -> bool:
    categoria = await session.get(Categoria, categoria_id)
    if categoria:
        await session.delete(categoria)
        await session.commit()
        return True
    return False

# ===== PRODUCTOS =====

async def crear_producto(session: AsyncSession, id_producto: str, nombre: str, precio: float, stock: int, id_categoria: int) -> Producto:
    producto = Producto(id_producto=id_producto, nombre=nombre, precio=precio, stock=stock, id_categoria=id_categoria)
    session.add(producto)
    await session.commit()
    await session.refresh(producto)
    return producto

async def obtener_producto_por_id(session: AsyncSession, producto_id: str) -> Optional[Producto]:
    return await session.get(Producto, producto_id)
async def buscar_productos(session: AsyncSession, query: str) -> List[Producto]:
    patron = f"%{query}%"

    statement = select(Producto).where(
        (Producto.nombre.ilike(patron)) |
        (Producto.id_producto.ilike(patron))
    )

    result = await session.execute(statement)
    return result.scalars().all()

async def obtener_todos_productos(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Producto]:
    result = await session.execute(select(Producto).offset(skip).limit(limit))
    return result.scalars().all()

async def obtener_productos_por_categoria(session: AsyncSession, categoria_id: int):
    result = await session.execute(select(Producto).where(Producto.id_categoria == categoria_id))
    return result.scalars().all()
async def obtener_productos_filtrados(session, categoria: int = 0, search: str = "") -> List[Producto]:
    stmt = select(Producto)

    if categoria != 0:
        stmt = stmt.where(Producto.id_categoria == categoria)

    if search:
        stmt = stmt.where(Producto.nombre.ilike(f"%{search}%"))

    result = await session.execute(stmt)
    return result.scalars().all()


def paginar_lista(lista, page: int, page_size: int):
    total = len(lista)
    start = (page - 1) * page_size
    end = start + page_size
    return lista[start:end], total


async def formatear_productos(session, productos):
    categorias = {c.id_categoria: c.tipo for c in await obtener_todas_categorias(session)}

    return [
        {
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "categoria_nombre": categorias.get(p.id_categoria, "Sin categoría")
        }
        for p in productos
    ]
async def actualizar_producto(session: AsyncSession, producto_id: str, nombre: str = None, precio: float = None, stock: int = None, id_categoria: int = None) -> Optional[Producto]:
    producto = await session.get(Producto, producto_id)
    if producto:
        if nombre is not None:
            producto.nombre = nombre
        if precio is not None:
            producto.precio = precio
        if stock is not None:
            producto.stock = stock
        if id_categoria is not None:
            producto.id_categoria = id_categoria
        await session.commit()
        await session.refresh(producto)
    return producto

async def actualizar_stock_producto(session: AsyncSession, producto_id: str, nueva_cantidad: int) -> Optional[Producto]:
    producto = await session.get(Producto, producto_id)
    if producto:
        producto.stock = nueva_cantidad
        await session.commit()
        await session.refresh(producto)
    return producto

async def sumar_stock_producto(session: AsyncSession, producto_id: str, cantidad: int) -> Optional[Producto]:
    producto = await session.get(Producto, producto_id)
    if producto:
        producto.stock += cantidad
        await session.commit()
        await session.refresh(producto)
    return producto

async def restar_stock_producto(session: AsyncSession, producto_id: str, cantidad: int) -> Optional[Producto]:
    producto = await session.get(Producto, producto_id)
    if producto and producto.stock >= cantidad:
        producto.stock -= cantidad
        await session.commit()
        await session.refresh(producto)
        return producto
    return None

async def eliminar_producto(session: AsyncSession, producto_id: str) -> bool:
    producto = await session.get(Producto, producto_id)
    if producto:
        await session.delete(producto)
        await session.commit()
        return True
    return False

# ===== CLIENTES =====

async def crear_cliente(session: AsyncSession, nombre: str, telefono: str, email: str) -> Cliente:
    cliente = Cliente(nombre=nombre, telefono=telefono, email=email)
    session.add(cliente)
    await session.commit()
    await session.refresh(cliente)
    return cliente

async def obtener_cliente_por_id(session: AsyncSession, cliente_id: int) -> Optional[Cliente]:
    return await session.get(Cliente, cliente_id)

async def obtener_todos_clientes(session: AsyncSession):
    statement = select(Cliente).order_by(Cliente.activo.desc(), Cliente.nombre.asc())
    result = await session.execute(statement)
    return result.scalars().all()

async def buscar_cliente_por_email(session: AsyncSession, email: str) -> Optional[Cliente]:
    result = await session.execute(select(Cliente).where(Cliente.email == email))
    return result.scalars().first()

async def actualizar_cliente(session: AsyncSession, cliente_id: int, nombre: str = None, telefono: str = None, email: str = None) -> Optional[Cliente]:
    cliente = await session.get(Cliente, cliente_id)
    if cliente:
        if nombre is not None:
            cliente.nombre = nombre
        if telefono is not None:
            cliente.telefono = telefono
        if email is not None:
            cliente.email = email
        await session.commit()
        await session.refresh(cliente)
    return cliente

async def eliminar_cliente(session: AsyncSession, cliente_id: int) -> bool:
    cliente = await session.get(Cliente, cliente_id)
    if cliente:
        await session.delete(cliente)
        await session.commit()
        return True
    return False

# ===== PROVEEDORES =====

async def crear_proveedor(session: AsyncSession, nit: str, nombre: str, direccion: str, ciudad: str, contacto: str) -> Proveedor:
    result = await session.execute(select(Proveedor).where(Proveedor.nit == nit))
    existente = result.scalar_one_or_none()
    if existente:
        raise ValueError("El NIT ya existe en la base de datos")

    proveedor = Proveedor(
        nit=nit,
        nombre=nombre,
        direccion=direccion,
        ciudad=ciudad,
        contacto=contacto
    )
    session.add(proveedor)

    try:
        await session.commit()
        await session.refresh(proveedor)
        return proveedor
    except IntegrityError:
        await session.rollback()
        raise ValueError("El NIT ya existe en la base de datos")

async def obtener_proveedor_por_nit(session: AsyncSession, nit: str) -> Optional[Proveedor]:
    result = await session.execute(select(Proveedor).where(Proveedor.nit == nit))
    return result.scalars().first()

async def obtener_todos_proveedores(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Proveedor]:
    result = await session.execute(select(Proveedor).offset(skip).limit(limit))
    return result.scalars().all()

async def obtener_proveedores_resumen(session: AsyncSession) -> List[Proveedor]:
    result = await session.execute(select(Proveedor))
    return result.scalars().all()

async def mover_proveedor(session: AsyncSession, nit: str) -> bool:
    proveedor = await session.get(Proveedor, nit)
    if not proveedor:
        return False
    proveedor_backup = ProveedorBackup(
        nit=proveedor.nit,
        nombre=proveedor.nombre,
        direccion=proveedor.direccion,
        ciudad=proveedor.ciudad,
        contacto=proveedor.contacto
    )
    session.add(proveedor_backup)
    await session.delete(proveedor)
    await session.commit()
    return True

async def obtener_proveedores_eliminados(session: AsyncSession) -> List[ProveedorBackup]:
    result = await session.execute(select(ProveedorBackup))
    return result.scalars().all()

async def recuperar_proveedor(session: AsyncSession, nit: str) -> bool:
    proveedor_backup = await session.get(ProveedorBackup, nit)
    if not proveedor_backup:
        return False
    proveedor = Proveedor(
        nit=proveedor_backup.nit,
        nombre=proveedor_backup.nombre,
        direccion=proveedor_backup.direccion,
        ciudad=proveedor_backup.ciudad,
        contacto=proveedor_backup.contacto
    )
    session.add(proveedor)
    await session.delete(proveedor_backup)
    await session.commit()
    return True

async def actualizar_proveedor(session: AsyncSession, nit: str, nombre: str = None, direccion: str = None, ciudad: str = None, contacto: str = None) -> Optional[Proveedor]:
    proveedor = await session.get(Proveedor, nit)
    if proveedor:
        if nombre is not None:
            proveedor.nombre = nombre
        if direccion is not None:
            proveedor.direccion = direccion
        if ciudad is not None:
            proveedor.ciudad = ciudad
        if contacto is not None:
            proveedor.contacto = contacto
        await session.commit()
        await session.refresh(proveedor)
    return proveedor

# ===== VALIDACIONES =====

async def categoria_existe(session: AsyncSession, categoria_id: int) -> bool:
    return await session.get(Categoria, categoria_id) is not None

async def producto_existe(session: AsyncSession, producto_id: str) ->bool:
    return await session.get(Producto, producto_id) is not None

async def cliente_existe(session: AsyncSession, cliente_id: int) -> bool:
    return await session.get(Cliente, cliente_id) is not None

async def proveedor_existe(session: AsyncSession, nit: str) -> bool:
    return await session.get(Proveedor, nit) is not None

async def verificar_stock_disponible(session: AsyncSession, producto_id: str, cantidad_requerida: int) -> bool:
    producto = await session.get(Producto, producto_id)
    if producto:
        return producto.stock >= cantidad_requerida
    return False
