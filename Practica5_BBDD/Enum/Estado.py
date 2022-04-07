from enum import Enum


class Estado(Enum):
    COMPRADO = "Comprado"
    VENDIDO = "Vendido"
    ESPERA = "En espera"
    CANCELADA = "Cancelada"
