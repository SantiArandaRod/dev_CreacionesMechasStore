
import fastapi
from typing import List, Optional, Any, Sequence

from sqlalchemy import false
from starlette import status

from modelSQL import *

def crear_categoria(session: Session, tipo: str, codigo: str) -> Categoria:
    """Crear una nueva categoría"""
    categoria = Categoria(tipo=tipo, codigo=codigo)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

def obtener_categoria_por_id(session: Session, categoria_id: int) -> Optional[Categoria]:
    """Obtener una categoría por su ID"""
    return session.get(Categoria, categoria_id)

def obtener_todas_categorias(session: Session, skip: int = 0, limit: int = 100) -> List[Categoria]:
    """Obtener todas las categorías con paginación"""
    statement = select(Categoria).offset(skip).limit(limit)
    return session.exec(statement).all()

def actualizar_categoria(session: Session, categoria_id: int, tipo: str = None, codigo: str = None) -> Optional[Categoria]:
    """Actualizar una categoría existente"""
    categoria = session.get(Categoria, categoria_id)
    if categoria:
        if tipo is not None:
            categoria.tipo=tipo
        if codigo is not None:
            categoria.codigo = codigo
        session.commit()
        session.refresh(categoria)
    return categoria

def eliminar_categoria(session: Session, categoria_id: int) -> bool:
    """Eliminar una categoría"""
    categoria = session.get(Categoria, categoria_id)
    if categoria:
        session.delete(categoria)
        session.commit()
        return True
    return False

def crear_producto(session: Session, id_producto: str, nombre: str, precio: float, stock: int, id_categoria: int) -> Producto:
    """Crear un nuevo producto"""
    producto = Producto(
        id_producto=id_producto,
        nombre=nombre,
        precio=precio,
        stock=stock,
        id_categoria=id_categoria
    )
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto

def obtener_producto_por_id(session: Session, producto_id: str) -> Optional[Producto]:
    """Obtener un producto por su ID"""
    return session.get(Producto, producto_id)

def obtener_todos_productos(session: Session, skip: int = 0, limit: int = 100) -> List[Producto]:
    """Obtener todos los productos con paginación"""
    statement = select(Producto).offset(skip).limit(limit)
    return session.exec(statement).all()

def obtener_productos_por_categoria(session: Session, categoria_id: int) -> List[Producto]:
    """Obtener productos de una categoría específica"""
    statement = select(Producto).where(Producto.id_categoria == categoria_id)
    return session.exec(statement).all()

def actualizar_producto(session: Session, producto_id: str, nombre: str = None, precio: float = None, stock: int = None, id_categoria: int = None) -> Optional[Producto]:
    """Actualizar un producto existente"""
    producto = session.get(Producto, producto_id)
    if producto:
        if nombre is not None:
            producto.nombre = nombre
        if precio is not None:
            producto.precio = precio
        if stock is not None:
            producto.stock = stock
        if id_categoria is not None:
            producto.id_categoria = id_categoria
        session.commit()
        session.refresh(producto)
    return producto

def actualizar_stock_producto(session: Session, producto_id: str, nueva_cantidad: int) -> Optional[Producto]:
    """Actualizar solo el stock de un producto"""
    producto = session.get(Producto, producto_id)
    if producto:
        producto.stock = nueva_cantidad
        session.commit()
        session.refresh(producto)
    return producto

def sumar_stock_producto(session: Session, producto_id: str, cantidad: int) -> Optional[Producto]:
    """Sumar cantidad al stock actual"""
    producto = session.get(Producto, producto_id)
    if producto:
        producto.stock += cantidad
        session.commit()
        session.refresh(producto)
    return producto

def restar_stock_producto(session: Session, producto_id: str, cantidad: int) -> Optional[Producto]:
    """Restar cantidad del stock actual (para ventas)"""
    producto = session.get(Producto, producto_id)
    if producto:
        if producto.stock >= cantidad:
            producto.stock -= cantidad
            session.commit()
            session.refresh(producto)
            return producto
        else:
            return None  # No hay suficiente stock
    return None

def eliminar_producto(session: Session, producto_id: str) -> bool:
    """Eliminar un producto"""
    producto = session.get(Producto, producto_id)
    if producto:
        session.delete(producto)
        session.commit()
        return True
    return False

def crear_cliente(session: Session, nombre: str, telefono: str, email: str) -> Cliente:
    """Crear un nuevo cliente"""
    cliente = Cliente(nombre=nombre, telefono=telefono, email=email)
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente

def obtener_cliente_por_id(session: Session, cliente_id: int) -> Optional[Cliente]:
    """Obtener un cliente por su ID"""
    return session.get(Cliente, cliente_id)

def obtener_todos_clientes(session: Session, skip: int = 0, limit: int = 100) -> List[Cliente]:
    """Obtener todos los clientes con paginación"""
    statement = select(Cliente).offset(skip).limit(limit)
    return session.exec(statement).all()

def buscar_cliente_por_email(session: Session, email: str) -> Optional[Cliente]:
    """Buscar cliente por email"""
    statement = select(Cliente).where(Cliente.email == email)
    return session.exec(statement).first()

def actualizar_cliente(session: Session, cliente_id: int, nombre: str = None, telefono: str = None, email: str = None) -> Optional[Cliente]:
    """Actualizar un cliente existente"""
    cliente = session.get(Cliente, cliente_id)
    if cliente:
        if nombre is not None:
            cliente.nombre = nombre
        if telefono is not None:
            cliente.telefono = telefono
        if email is not None:
            cliente.email = email
        session.commit()
        session.refresh(cliente)
    return cliente

def eliminar_cliente(session: Session, cliente_id: int) -> bool:
    """Eliminar un cliente"""
    cliente = session.get(Cliente, cliente_id)
    if cliente:
        session.delete(cliente)
        session.commit()
        return True
    return False

def crear_proveedor(session: Session, nit: str, nombre: str,  direccion: str, ciudad: str,contacto: str) -> Proveedor:
    """Crear un nuevo proveedor"""
    print(123)
    proveedor = Proveedor(
        nit=nit,
        nombre=nombre,
        direccion=direccion,
        ciudad=ciudad,
        contacto=contacto
    )
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor

def obtener_proveedor_por_nit(session: Session, nit: str) -> Optional[Proveedor]:
    """Obtener un proveedor por su NIT"""
    return session.get(Proveedor, nit)

def obtener_todos_proveedores(session: Session, skip: int = 0, limit: int = 100) -> List[Proveedor]:
    """Obtener todos los proveedores con paginación"""
    statement = select(Proveedor).offset(skip).limit(limit)
    return session.exec(statement).all()

def obtener_proveedores_resumen(session: Session) -> List[Proveedor]:
    return session.exec(select(Proveedor)).all()

def mover_proveedor(session: Session, nit: str) -> bool:
    """Mueve un proveedor a otra tabla como backup"""
    proveedor = session.get(Proveedor, nit)
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
    session.delete(proveedor)
    session.commit()

    return True
def obtener_proveedores_eliminados(session: Session) -> List[ProveedorBackup]:
    """Obtener todos los proveedores eliminados"""
    return session.exec(select(ProveedorBackup)).all()


def recuperar_proveedor(session: Session, nit: str) -> bool:
    proveedor_backup = session.get(ProveedorBackup, nit)
    if not proveedor_backup:
        return False
    proveedor=Proveedor(
        nit=proveedor_backup.nit,
        nombre=proveedor_backup.nombre,
        direccion=proveedor_backup.direccion,
        ciudad=proveedor_backup.ciudad,
        contacto=proveedor_backup.contacto
    )

    session.add(proveedor)
    session.delete(proveedor_backup)
    session.commit()
    return True

def actualizar_proveedor(session: Session,nit:str,nombre: str = None, direccion:str = None, ciudad:str = None, contacto:str = None) -> Optional[Proveedor]:
    """Actualizar un proveedor"""
    proveedor= session.get(Proveedor,nit)
    if proveedor:
        if nombre is not None:
            proveedor.nombre = nombre
        if direccion is not None:
            proveedor.direccion = direccion
        if ciudad is not None:
            proveedor.ciudad = ciudad
        if contacto is not None:
            proveedor.contacto = contacto
        session.commit()
        session.refresh(proveedor)
    return proveedor

# ===== VALIDACIONES ÚTILES =====
def categoria_existe(session: Session, categoria_id: int) -> bool:
    """Verificar si una categoría existe"""
    return session.get(Categoria, categoria_id) is not None

def producto_existe(session: Session, producto_id: str) -> bool:
    """Verificar si un producto existe"""
    return session.get(Producto, producto_id) is not None

def cliente_existe(session: Session, cliente_id: int) -> bool:
    """Verificar si un cliente existe"""
    return session.get(Cliente, cliente_id) is not None

def proveedor_existe(session: Session, nit: str) -> bool:
    """Verificar si un proveedor existe"""
    return session.get(Proveedor, nit) is not None

def verificar_stock_disponible(session: Session, producto_id: str, cantidad_requerida: int) -> bool:
    """Verificar si hay suficiente stock para una operación"""
    producto = session.get(Producto, producto_id)
    if producto:
        return producto.stock >= cantidad_requerida
    return False

