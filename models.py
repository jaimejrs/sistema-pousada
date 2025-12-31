from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import streamlit as st
import sys

Base = declarative_base()

# TABELAS
class Quarto(Base):
    __tablename__ = 'quartos'
    id = Column(Integer, primary_key=True)
    numero = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False)
    reservas = relationship("Reserva", back_populates="quarto")

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String)
    telefone = Column(String)
    cpf = Column(String, unique=True)
    reservas = relationship("Reserva", back_populates="cliente")

class Reserva(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True)
    data_checkin = Column(DateTime, nullable=False) 
    data_checkout = Column(DateTime, nullable=False)
    tipo_tarifa = Column(String)
    valor_total = Column(Float)
    status = Column(String, default='Ativa')
    
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    quarto_id = Column(Integer, ForeignKey('quartos.id'))
    
    cliente = relationship("Cliente", back_populates="reservas")
    quarto = relationship("Quarto", back_populates="reservas")

# CONEXÃO NUVEM
try:
    db_url = st.secrets["db"]["url"]
    
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    
except Exception as e:
    st.error(f"❌ Erro: Não foi possível conectar ao banco de dados na nuvem.\nDetalhe: {e}")
    st.stop() 

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)