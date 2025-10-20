import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Cargar variables de entorno
load_dotenv()

# Intentar obtener la URL desde .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no existe, usar SQLite local por defecto
if not DATABASE_URL:
    print("⚠️ No se detectó DATABASE_URL, usando base de datos local SQLite.")
    DATABASE_URL = "sqlite:///./local_test.db"

# Crear el engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Crear todas las tablas definidas por tus modelos
def init_db():
    SQLModel.metadata.create_all(engine)

# Generador de sesión (para FastAPI)
def get_session():
    with Session(engine) as session:
        yield session
