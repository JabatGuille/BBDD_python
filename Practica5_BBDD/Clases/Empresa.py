class Empresa:

    def __init__(self, empresa):
        self.empresa = empresa
        self.compras = {}
        self.ventas = {}

    def ayadir_compras(self, compra):
        self.compras[compra.id] = compra

    def ayadir_ventas(self, venta):
        self.ventas[venta.id] = venta
