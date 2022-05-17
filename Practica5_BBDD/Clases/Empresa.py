class Empresa:

    def __init__(self, empresa):
        self.empresa = empresa
        self.compras = {}
        self.ventas = {}

    def ayadir_compras(self, compra):
        self.compras[compra.id] = compra

    def quitar_compra(self, compra):
        self.compras.pop(compra.id)

    def ayadir_ventas(self, venta):
        self.ventas[venta.id] = venta

    def quitar_venta(self, venta):
        self.ventas.pop(venta.id)
