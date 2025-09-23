
from sqlmodel import Field, SQLModel, create_engine, Session, select
DATABASE_URL = ""
engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)