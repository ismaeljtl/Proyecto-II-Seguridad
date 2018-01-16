# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tarjetas(Base):

    __tablename__ = 'tarjetas'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True)
    identificacion = Column(String(20))
    nombre = Column(String(250))
    numero_tarjeta = Column(String(30))
    vencimiento_mes = Column(Integer())
    vecimiento_año = Column(Integer())
    cvv = Column(String(5))
    saldo = Column(Float(asdecimal=True))
    movimientos = relationship('Movimientos', back_populates='tarjeta')


class Movimientos(Base):

    __tablename__ = 'movimientos'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = Column(Integer, primary_key=True)
    id_tarjeta = Column(Integer, ForeignKey('tarjetas.id'))
    monto_movimiento = Column(Float(asdecimal=True))
    tarjeta = relationship('Tarjetas', back_populates='movimientos')