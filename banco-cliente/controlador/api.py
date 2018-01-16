# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.response import json
import sys
sys.path.append("..")

from modelo.modelo import Modelo

app = Sanic(__name__)


@app.post('/comprar')
async def post_handler(request):
    modelo = Modelo()
    respuesta = await modelo.realizarPago(request.json)
    return json(respuesta)
