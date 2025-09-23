

from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Session, select


class Categoria(SQLModel, table=True):
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    nombre: str


class Producto(SQLModel, table=True):
    id_producto: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    stock: int
    id_categoria: int = Field(foreign_key="categoria.id_categoria")


class Cliente(SQLModel, table=True):
    id_cliente: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    email: str


class Venta(SQLModel, table=True):
    id_venta: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime
    id_cliente: int = Field(foreign_key="cliente.id_cliente")
    total_venta: float


class DetalleVenta(SQLModel, table=True):
    id_detalle_venta: Optional[int] = Field(default=None, primary_key=True)
    id_venta: int = Field(foreign_key="venta.id_venta")
    id_producto: int = Field(foreign_key="producto.id_producto")
    cantidad: int
    precio_unidad: float


class Proveedor(SQLModel, table=True):
    nit: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    direccion: str
    ciudad: str


class Compra(SQLModel, table=True):
    id_compra: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime
    total_compra: float
    id_proveedor: int = Field(foreign_key="proveedor.nit")


class DetalleCompra(SQLModel, table=True):
    id_detalle_compra: Optional[int] = Field(default=None, primary_key=True)
    id_compra: int = Field(foreign_key="compra.id_compra")
    id_producto: int = Field(foreign_key="producto.id_producto")
    cantidad: int
    precio_unidad: float

