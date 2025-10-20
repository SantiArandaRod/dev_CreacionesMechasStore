
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Session, select


class Categoria(SQLModel, table=True):
    id_categoria: int = Field(default=None, primary_key=True)
    tipo: str
    codigo: str


class Producto(SQLModel, table=True):
    id_producto: str = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    stock: int
    id_categoria: int = Field(foreign_key="categoria.id_categoria")


class Cliente(SQLModel, table=True):
    id_cliente: int = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    email: str

    
class Venta(SQLModel, table=True):
    id_venta_pk: str = Field(primary_key=True)
    fecha: datetime
    documento_fk: int = Field(foreign_key="cliente.documento_pk")
    total: float


class DetalleVenta(SQLModel, table=True):
    id_detalleventa_pk: int = Field(primary_key=True)
    id_venta_fk: str = Field(foreign_key="venta.id_venta_pk")
    isbn_fk: str
    cantidad: int
    precio_unidad: float



class Proveedor(SQLModel, table=True):
    nit: str = Field(default=None, primary_key=True)
    nombre: str
    contacto: str
    direccion: str
    ciudad: str


class Compra(SQLModel, table=True):
    id_compra: int = Field(default=None, primary_key=True)
    fecha: datetime
    nit: str = Field(foreign_key="proveedor.nit")


class DetalleCompra(SQLModel, table=True):
    id_detalle_compra: int = Field(default=None, primary_key=True)
    id_compra: int = Field(foreign_key="compra.id_compra")
    id_producto: str = Field(foreign_key="producto.id_producto")
    cantidad: int
    precio_unidad: float



