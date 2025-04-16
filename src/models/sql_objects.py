from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Date, Integer

# Definir el modelo base
Base = declarative_base()

class sql_objects(Base):
    __tablename__ = 'resultados'  # Nombre ficticio, no se usará para mapeo en una tabla real

    # Definición de columnas
    ID = Column(Integer, primary_key=True)
    Schema = Column(String)
    Name = Column(String)
    Object_Key = Column(String)
    Sql_Object = Column(String)
    Creation_Date = Column(Date)
    Modification_Date = Column(Date)
    
def __repr__(self) -> str:
    return f"<SQL_Objects(ID={self.ID}, Schema={self.Schema}, Name={self.Name}, Object_Key={self.Object_Key}, Sql_Object={self.Sql_Object}, Creation_Date={self.Creation_Date},Modification_Date={self.Modification_Date})>"
