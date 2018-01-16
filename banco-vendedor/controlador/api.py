# -*- coding: utf-8 -*-

from sanic import Sanic
import sys
sys.path.append("..")

from modelo.modelo import Modelo

app = Sanic(__name__)


@app.websocket('/compra/confirmacion')
async def confimarCompra(request, ws):
	modelo = Modelo()
	data = await ws.recv()
	print(data)
	respuesta = await modelo.realizarMovimiento(data)
	await ws.send(respuesta)