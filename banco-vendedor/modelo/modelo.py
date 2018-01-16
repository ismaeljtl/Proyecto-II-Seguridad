# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from dao import dao
from sqlalchemy.orm import sessionmaker
import ujson
from decimal import *
import requests
import traceback

class Modelo(object):

    def __init__(self):
        engine = create_engine('mysql+pymysql://root:12345@seguridad-bd:3306/banco_vendedor?charset=utf8', 
                                echo=False, convert_unicode=True)
        dao.Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    async def realizarMovimiento(self, json):
        sesion = self.Session()

        data = ujson.loads(json)

        if data["estatus"] != "200":
            return await self.notificarTransaccion(data, sesion, "500")

        try:
            tarjeta = sesion.query(dao.Tarjetas).filter(dao.Tarjetas.id == data["id_vendedor"]).all()

            if (len(tarjeta) == 0):
                return "501"
            else:
                tarjeta = tarjeta[0]
        
            movimiento = dao.Movimientos()
            movimiento.id_tarjeta = tarjeta.id
            movimiento.monto_movimiento = data["monto"]
            tarjeta.saldo = Decimal(tarjeta.saldo) + Decimal(data["monto"])
            sesion.add(movimiento)

            resultado = await self.notificarTransaccion(data, sesion, "200")

        except (KeyError, AttributeError, IndexError) as e:
            sesion.rollback()
            await self.notificarTransaccion(data, sesion, "500")
            resultado = "500"

        return resultado

    async def notificarTransaccion(self, datos, sesion, estatus):
        respuesta = dict(estatus=estatus)
        url = datos.pop("direccion_respuesta")
        respuesta.update(datos)

        peticion = requests.post(url, data=ujson.dumps(respuesta), cert=("/certificados/clienteFirmado.crt", "/certificados/cliente.key"))


        if peticion.status_code == requests.codes.ok:
            sesion.commit()
            return "200"
        else:
            sesion.rollback()
            return "500"
