# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from dao import dao
from sqlalchemy.orm import sessionmaker
import ujson
from decimal import *
import requests
import websockets
import certifi
import ssl

class Modelo(object):

    def __init__(self):
        engine = create_engine('mysql+pymysql://root:12345@seguridad-bd:3306/banco_cliente?charset=utf8',
                                echo=False, convert_unicode=True)
        dao.Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    async def realizarPago(self, data):
        sesion = self.Session()

        try:
            tarjeta = sesion.query(dao.Tarjetas).filter(dao.Tarjetas.numero_tarjeta == data["numero_tarjeta"], 
                                                      dao.Tarjetas.identificacion == data["identificacion"],
                                                      dao.Tarjetas.cvv == data["cvv"],
                                                      dao.Tarjetas.vencimiento_mes == data["fecha_vencimiento_mes"],
                                                      dao.Tarjetas.vecimiento_año == data["fecha_vencimiento_año"],
                                                      dao.Tarjetas.nombre == data["nombre_tarjetahabiente"]).all()

            if len(tarjeta) == 0:
                return "No existe ese cliente"
            else:
                tarjeta = tarjeta[0]
        
            if Decimal(tarjeta.saldo) >= Decimal(data["monto"]):
                movimiento = dao.Movimientos()
                movimiento.id_tarjeta = tarjeta.id
                movimiento.monto_movimiento = Decimal(data["monto"]) * -1
                tarjeta.saldo = Decimal(tarjeta.saldo) - Decimal(data["monto"])
                sesion.add(movimiento)
                
                respuestaBancoVendedor = await self.notificarTransaccionSocket(data, sesion, "200")
                if respuestaBancoVendedor == "200":
                    return "Transacción exitosa"
                else:
                    return "Error en los datos"

            else:
                await self.notificarTransaccionSocket(data, sesion, "500")
                return "Saldo insuficiente"

        except (KeyError, AttributeError) as e:
            print(str(e))
            await self.notificarTransaccionSocket(data, sesion, "500")
            return "Datos invalidos"

    async def notificarTransaccionSocket(self, datos, sesion, estatus):
        respuesta = dict(estatus=estatus)
        datos.pop("numero_tarjeta")
        datos.pop("cvv")
        datos.pop("nombre_tarjetahabiente")
        datos.pop("fecha_vencimiento_mes")
        datos.pop("fecha_vencimiento_año")
        datos.pop("identificacion")
        respuesta.update(datos)

        contexto = ssl.create_default_context(cafile=certifi.where())

        async with websockets.connect('wss://bancovendedor.com/compra/confirmacion', ssl=contexto) as websocket:
            await websocket.send(ujson.dumps(respuesta))
            respuesta = await websocket.recv()

            if sesion.new or sesion.dirty or sesion.deleted:
                if respuesta == "200" and estatus == "200":
                    sesion.commit()
                else:
                    sesion.rollback()

            return respuesta
