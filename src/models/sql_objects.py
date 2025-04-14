from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Date, Integer

# Definir el modelo base
Base = declarative_base()

class sql_objects(Base):
    __tablename__ = 'resultados'  # Nombre ficticio, no se usará para mapeo en una tabla real

    # Definición de columnas
    ID = Column(Integer, primary_key=True)
    Esquema = Column(String)
    Nombre = Column(String)
    ClaveObjeto = Column(String)
    TipoObjetoSQL = Column(String)
    FechaCreacion = Column(Date)
    FechaModificacion = Column(Date)
    
def __repr__(self) -> str:
    return f"<SQL_Objects(ID={self.ID}, Esquema={self.Esquema}, Nombre={self.Nombre}, ClaveObjeto={self.ClaveObjeto}, TipoObjetoSQL={self.TipoObjetoSQL}, FechaCreacion={self.FechaCreacion},FechaModificacion={self.FechaModificacion})>"
